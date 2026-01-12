"""
title: Generic Multi-Knowledge Search Tool
author: Beau D'Amore www.damore.ai
version: 2.0.0
description: Generic reusable tool to search specific knowledge bases. Copy this tool, rename it (e.g., "Father Elias Search", "Saint Augustine Search"), and configure the default_knowledge_base setting with a comma-separated list of KB names for that specific model/purpose.
requirements: fastapi
"""

import asyncio
from typing import Any, Dict, List, Optional

from fastapi import Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from open_webui.models.knowledge import Knowledges, KnowledgeUserModel
from open_webui.models.users import Users
from open_webui.routers.retrieval import QueryCollectionsForm, query_collection_handler


class Tools:

    class Valves(BaseModel):
        """Configuration parameters for the knowledge search tool"""

        default_knowledge_base: str = Field(
            default="",
            description="Knowledge base name(s) to search. Use comma-separated list for multiple KBs (e.g., 'Nicene Fathers,Confessions' or 'Employee Handbook'). This defines what content this tool instance can access.",
        )
        max_results: int = Field(
            default=5,
            description="Top K: Maximum number of results to retrieve. ALWAYS overrides global setting in both hybrid and standard search modes.",
        )
        reranker_results: int = Field(
            default=0,
            description="Top K Reranker: Results to retain after reranking (0 uses global default). ONLY works when global 'Hybrid Search' is enabled in Settings > Documents > Retrieval. Ignored in standard search mode.",
        )
        relevance_threshold: float = Field(
            default=0.0,
            description="Relevance Threshold: Minimum score filter (0.0-1.0, where 0.0 uses global default). ONLY works when global 'Hybrid Search' is enabled. Ignored in standard search mode.",
        )
        enable_hybrid_search: bool = Field(
            default=True,
            description="Enable hybrid search (semantic + lexical/BM25). REQUIRES global 'Hybrid Search' enabled in Settings > Documents. When True: uses hybrid if globally enabled. When False: forces standard vector-only search (still uses 'max_results' override).",
        )
        hybrid_bm25_weight: float = Field(
            default=0.5,
            description="BM25 Weight (0.0-1.0): Balance between semantic (0.0) and lexical/keyword (1.0) search. ONLY works when global 'Hybrid Search' is enabled. 0.5 = balanced (default). Lower values favor meaning/context, higher values favor exact keyword matching. Ignored in standard search mode.",
        )
        enable_enriched_texts: bool = Field(
            default=True,
            description="Enrich BM25 Text: Adds filenames, titles, section headings, and source URLs to lexical search index. ONLY works when global 'Hybrid Search' is enabled. Improves recall when searching by document metadata (e.g., 'find document about X' or 'search in Chapter 5'). Ignored in standard search mode.",
        )
        include_distances: bool = Field(
            default=True,
            description="Include distance/similarity scores in the output when not using persona mode.",
        )
        enable_debug_output: bool = Field(
            default=True,
            description="Include debug information in responses",
        )

    def __init__(self):
        self.valves = self.Valves()

    async def search_knowledge(
        self,
        query: str,
        __user__: Optional[dict] = None,
        __request__: Optional[Any] = None,
        __event_emitter__=None,
    ) -> str:
        """
        Search the pre-configured knowledge base(s) for relevant information.

        **THIS IS THE ONLY METHOD YOU SHOULD CALL.**
        Do not call any other methods (like _perform_search or _format_results).

        This tool is pre-configured with specific knowledge base(s) in its settings.
        Simply provide your search query and the tool handles everything automatically.

        Args:
            query: What to search for (e.g., "forgiveness in the Bible", "grace and mercy")

        Returns:
            Relevant passages and information from the configured knowledge base(s)

        Example:
            search_knowledge(query="What does the Bible say about forgiveness?")
        """
        eventer = __event_emitter__ or (lambda *args, **kwargs: asyncio.sleep(0))

        try:
            request = KnowledgeRepository.require_request(__request__)
            user = await KnowledgeRepository.resolve_user(__user__)
        except ValueError as exc:
            message = f"❌ {exc}"
            await KnowledgeRepository.emit_error(eventer, str(exc))
            return message

        if self.valves.default_knowledge_base:
            kb_name = self.valves.default_knowledge_base
        else:
            kb_name = ""

        if not kb_name:
            await KnowledgeRepository.emit_error(eventer, "No default knowledge base configured")
            return "❌ No default knowledge base configured. Set one in the tool configuration."

        kb_names = [name.strip() for name in kb_name.split(",") if name.strip()]

        if len(kb_names) > 1:
            await KnowledgeRepository.emit_status(
                eventer, f"Searching {len(kb_names)} knowledge bases..."
            )
            all_results: List[str] = []

            for kb_name in kb_names:
                try:
                    await KnowledgeRepository.emit_status(eventer, f"Searching '{kb_name}'...")

                    kb_model = await KnowledgeRepository.find_by_name(
                        user.id, kb_name
                    )
                    if not kb_model:
                        all_results.append(
                            f"## '{kb_name}'\n❌ Knowledge base not found\n"
                        )
                        continue

                    search_data = await KnowledgeRepository.query_knowledge_base(
                        request=request,
                        user=user,
                        kb_id=kb_model.id,
                        query=query,
                        limit=self.valves.max_results,
                        valves=self.valves,
                    )
                    kb_results = await KnowledgeRepository.format_results(
                        search_data, query, kb_name, show_header=False, valves=self.valves
                    )
                    all_results.append(kb_results)

                except Exception as exc:
                    all_results.append(f"## '{kb_name}'\n❌ Error: {exc}\n")

            final_output = f"🔍 **Search Results for: '{query}'**\n\n" + "".join(
                all_results
            )
            await KnowledgeRepository.emit_result(eventer, final_output)
            await KnowledgeRepository.emit_status(eventer, "Multi-search complete", done=True)
            return final_output

        kb_name = kb_names[0]

        debug_info = ""
        if self.valves.enable_debug_output:
            debug_info = f"""🔧 **Debug Information**:
- Query: '{query}'
- Knowledge Base: '{kb_name}'
- Max Results (k): {self.valves.max_results}
- Reranker Results (k_reranker): {self.valves.reranker_results}
- Relevance Threshold (r): {self.valves.relevance_threshold}
- Hybrid Search: {self.valves.enable_hybrid_search}
- BM25 Weight: {self.valves.hybrid_bm25_weight}
- Enriched BM25 Text: {self.valves.enable_enriched_texts}

"""

        try:
            await KnowledgeRepository.emit_status(eventer, f"Searching knowledge base '{kb_name}'...")

            await KnowledgeRepository.emit_status(eventer, "Looking up knowledge base...")
            kb_model = await KnowledgeRepository.find_by_name(user.id, kb_name)

            if not kb_model:
                available_kbs = await KnowledgeRepository.load_by_user(user.id, "read")
                kb_names_list = [kb.name or "Unknown" for kb in available_kbs]
                error_msg = (
                    f"Knowledge base '{kb_name}' not found.\nAvailable knowledge bases: "
                    + ", ".join(kb_names_list)
                )
                await KnowledgeRepository.emit_error(eventer, error_msg)
                return debug_info + f"❌ {error_msg}"

            await KnowledgeRepository.emit_status(eventer, "Executing search...")
            search_data = await KnowledgeRepository.query_knowledge_base(
                request=request,
                user=user,
                kb_id=kb_model.id,
                query=query,
                limit=self.valves.max_results,
                valves=self.valves,
            )

            await KnowledgeRepository.emit_status(eventer, "Processing results...")
            results = await KnowledgeRepository.format_results(search_data, query, kb_name, valves=self.valves)

            final_output = debug_info + results

            await KnowledgeRepository.emit_result(eventer, final_output)
            await KnowledgeRepository.emit_status(eventer, "Search complete", done=True)

            return final_output

        except Exception as exc:
            error_msg = f"Search failed: {exc}"
            await KnowledgeRepository.emit_error(eventer, error_msg)
            return debug_info + f"❌ {error_msg}"


class KnowledgeRepository:
    """Central helper for loading knowledge bases; kept outside Tools to avoid tool exposure."""

    @staticmethod
    async def load_by_user(
        user_id: Any, permission: str = "read"
    ) -> List[KnowledgeUserModel]:
        knowledge = await run_in_threadpool(
            Knowledges.get_knowledge_bases_by_user_id, user_id, permission
        )
        return knowledge or []

    @staticmethod
    async def find_by_name(
        user_id: Any, kb_identifier: str, permission: str = "read"
    ) -> Optional[KnowledgeUserModel]:
        knowledge_bases = await KnowledgeRepository.load_by_user(user_id, permission)
        if not knowledge_bases:
            return None

        normalized = kb_identifier.strip().lower()
        by_name: Dict[str, KnowledgeUserModel] = {
            (kb.name or "").strip().lower(): kb for kb in knowledge_bases if kb.name
        }
        if normalized in by_name:
            return by_name[normalized]

        by_id: Dict[str, KnowledgeUserModel] = {kb.id: kb for kb in knowledge_bases}
        return by_id.get(kb_identifier)

    # -------- Context resolution helpers (moved from Tools) -------- #
    @staticmethod
    async def resolve_user(__user__: Optional[dict]) -> Any:
        if not __user__ or not __user__.get("id"):
            raise ValueError("User context with an 'id' is required")
        user = await run_in_threadpool(Users.get_user_by_id, str(__user__["id"]))
        if not user:
            raise ValueError("Unable to resolve OpenWebUI user")
        return user

    @staticmethod
    def require_request(__request__: Optional[Any]) -> Any:
        if __request__ is None:
            raise ValueError("Request context is required inside OpenWebUI")
        if not isinstance(__request__, Request):
            raise ValueError("Invalid request context provided")
        return __request__

    # -------- Event emitter helpers (moved from Tools) -------- #
    @staticmethod
    async def emit_status(eventer, msg: str, done: bool = False, hidden: bool = False):
        await eventer(
            {
                "type": "status",
                "data": {
                    "description": msg,
                    "done": done,
                    "hidden": hidden,
                },
            }
        )

    @staticmethod
    async def emit_error(eventer, msg: str, done: bool = True, hidden: bool = False):
        await eventer(
            {
                "type": "error",
                "data": {
                    "description": msg,
                    "done": done,
                    "hidden": hidden,
                },
            }
        )

    @staticmethod
    async def emit_result(eventer, content: str, done: bool = True, hidden: bool = False):
        await eventer(
            {
                "type": "result",
                "data": {
                    "description": content,
                    "done": done,
                    "hidden": hidden,
                },
            }
        )

    # -------- Search and formatting helpers (moved from Tools) -------- #
    @staticmethod
    async def query_knowledge_base(
        request: Any,
        user: Any,
        kb_id: str,
        query: str,
        limit: int,
        valves: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Query knowledge base with explicit parameter passing to override global document settings.
        
        Note: Global ENABLE_RAG_HYBRID_SEARCH must be enabled for hybrid search to work.
        Tool valves provide override values when the feature is enabled globally.
        """
        max_results = getattr(valves, "max_results", limit) if valves else limit
        
        # Build form with ALL parameters explicitly to ensure overrides work
        form_kwargs: Dict[str, Any] = {
            "collection_names": [kb_id],
            "query": query,
            "k": max(limit, max_results),
            # Explicitly pass hybrid flag - tells handler to use hybrid path if globally enabled
            "hybrid": getattr(valves, "enable_hybrid_search", None) if valves else None,
            # Always pass reranker param (handler uses it or falls back to config)
            "k_reranker": getattr(valves, "reranker_results", None) if valves else None,
            # Always pass relevance threshold (handler uses it or falls back to config)
            "r": getattr(valves, "relevance_threshold", None) if valves else None,
            # Pass BM25 weight for hybrid search (0-1, where 0=semantic, 1=lexical)
            "hybrid_bm25_weight": getattr(valves, "hybrid_bm25_weight", None) if valves else None,
            # Pass enriched text flag (improves lexical recall in hybrid search)
            "enable_enriched_texts": getattr(valves, "enable_enriched_texts", None) if valves else None,
        }
        
        form = QueryCollectionsForm(**form_kwargs)
        return await query_collection_handler(request=request, form_data=form, user=user)

    @staticmethod
    async def format_results(
        data: Dict[str, Any], query: str, kb_name: str, show_header: bool = True, valves: Optional[Any] = None
    ) -> str:
        documents = data.get("documents", [])
        distances = data.get("distances", [])
        if not documents or not documents[0]:
            return f"❌ No results found for '{query}' in knowledge base '{kb_name}'"
        doc_list = documents[0]
        dist_list = distances[0] if distances and distances[0] else []
        result_count = len(doc_list)

        include_distances = getattr(valves, "include_distances", True) if valves else True

        # Return clean excerpts - global RAG template handles persona framing
        output = ""
        for idx, doc in enumerate(doc_list):
            output += f"{doc}\n\n"
        return output.strip()
