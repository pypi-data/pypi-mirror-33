#ifndef GXX_POOL_H
#define GXX_POOL_H

//#include <mem/sysalloc.h>

#include <gxx/dlist.h>
#include <gxx/datastruct/slist_head.h>
#include <gxx/vector.h>

namespace gxx {

	//template <size_t PageSize, typename Allocator = gxx::allocator<char>>
	//class page_pool {
	//	//gxx::vector<void*> pages;
	//	
	//public:
	//	constexpr static size_t pageSize = PageSize; 
//
	//	void* allocate_page() {
	//		//dprln("page_pool::allocate_page");
	//		void* ret = Allocator().allocate(pageSize);
	//		//pages.emplace_back(ret);
	//		return ret;
	//	}	
//
	//	~page_pool() {
	//		//for(auto p : pages) {
	//		//	sysfree(p);
	//		//}
	//	}	
	//};
//
	//template<typename T, size_t TotalOnPage>
	//class block_pool : public page_pool<sizeof(T) * TotalOnPage> {
	//private:
	//	using Parent = page_pool<sizeof(T) * TotalOnPage>;
	//	slist_head head;
//
	//public: 
	//	block_pool() {
	//		slist_init(&head);
	//	};
//
	//	T* allocate() {
	//		if (head.next == nullptr) formatNewPage();
	//		T* ret = reinterpret_cast<T*>(head.next);
	//		slist_del(head.next, &head);
	//		return ret;
	//	}
//
	//	template<typename ... Args>
	//	T* emplace(Args ... args) {
	//		T* ptr = allocate();
	//		gxx::constructor(ptr, std::forward<Args>(args) ...);
	//		return ptr;
	//	}
//
	//	void release(T* ptr) {
	//		slist_head* node = reinterpret_cast<slist_head*>(ptr);
	//		slist_add_next(node, &head);
	//	}
//
	//private:
	//	void formatNewPage() {
	//		assert(head.next == nullptr);
	//		void* page = Parent::allocate_page();
	//		
	//		char * end = (char*)page + Parent::pageSize;
	//		for(char* pos = (char*)page; pos != end; pos += sizeof(T)) {
	//			slist_add_next(reinterpret_cast<slist_head*>(pos), &head);
	//		}
	//	}
	//};
}

#endif