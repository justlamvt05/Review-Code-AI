from modules.search.repository import SearchRepository
from modules.search.schemas import (
    SearchType,
    SearchResponse,
    ProjectSearchResult,
    ReviewSearchResult,
    UserSearchResult,
)


class SearchService:
    def __init__(self, repository: SearchRepository):
        self.repository = repository

    def search(
        self,
        query: str,
        search_type: SearchType = SearchType.ALL,
        limit: int = 20,
        offset: int = 0,
    ) -> SearchResponse:
        """
        Tìm kiếm tổng hợp hoặc theo loại.

        Args:
            query: Từ khoá tìm kiếm.
            search_type: Loại tìm kiếm (project/review/user/all).
            limit: Số lượng kết quả tối đa mỗi loại.
            offset: Vị trí bắt đầu.

        Returns:
            SearchResponse chứa kết quả tìm kiếm.
        """
        projects = []
        reviews = []
        users = []
        total = 0

        # Search Projects
        if search_type in (SearchType.ALL, SearchType.PROJECT):
            project_items, project_total = self.repository.search_projects(
                query, limit, offset,
            )
            projects = [
                ProjectSearchResult.model_validate(p) for p in project_items
            ]
            total += project_total

        # Search Reviews
        if search_type in (SearchType.ALL, SearchType.REVIEW):
            review_items, review_total = self.repository.search_reviews(
                query, limit, offset,
            )
            reviews = [
                ReviewSearchResult.model_validate(r) for r in review_items
            ]
            total += review_total

        # Search Users
        if search_type in (SearchType.ALL, SearchType.USER):
            user_items, user_total = self.repository.search_users(
                query, limit, offset,
            )
            users = [
                UserSearchResult.model_validate(u) for u in user_items
            ]
            total += user_total

        return SearchResponse(
            query=query,
            type=search_type,
            projects=projects,
            reviews=reviews,
            users=users,
            total_results=total,
        )
