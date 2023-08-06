#ifndef GXX_MEMORY_HEAP_H
#define GXX_MEMORY_HEAP_H

#include <gxx/print.h>
#include <gxx/dlist.h>
#include <new>

namespace gxx {
	namespace memory {
		struct freenode {
			dlist_head lnk;
			size_t sz;
			freenode(size_t sz) : sz(sz) {}
			void* end() { return reinterpret_cast<char*>(this) + sz; }
			gxx::buffer block() { return gxx::buffer((char*)this, sz); }
			char* start() {
				return reinterpret_cast<char*>(this) + sizeof(size_t);
			}
		};
		
		using freelist = gxx::dlist<freenode, &freenode::lnk>;
			
		class heap {
		public:
			freelist fl;
			
			heap() {}
			heap(void* ptr, size_t sz) {
				engage_block(ptr, sz);
			}

			template<typename T> 
			class allocator {
				heap& href;
			public:
				using value_type = T;
				using size_type = size_t;

				allocator(heap& href) : href(href) {}

				T* allocate(size_t n) { 
					void* ret = href.allocate(n * sizeof(T));
					if (ret == nullptr) throw std::bad_alloc();
					return (T*)ret; 
				} 
				void deallocate(T* ptr) { return href.deallocate(ptr); } 
				void deallocate(T* ptr, size_t n) { return href.deallocate(ptr); } 
			};

			void engage_block(void* ptr, size_t sz) {
				assert(sz >= sizeof(freenode));
				char* endblk = (char*) ptr + sz;

				auto it = fl.begin();
				auto eit = fl.end();

				for(;it != eit;++it) if ((char*)&*it > (char*)ptr) break;
				 
				auto itnext = it;
				auto itprev = (--it);

				bool union_with_prev = !(itprev == eit) && (char*)itprev->end() == (char*)ptr;
				bool union_with_next = !(itnext == eit) && (char*)&*itnext 		== (char*)endblk;			

				if (union_with_prev && union_with_next) {
					itprev->sz += sz + itnext->sz;
					freelist::unbind(*itnext);
					return;
				}

				if (union_with_prev) {
					itprev->sz += sz;
					return;
				}

				freenode* node = new (ptr) freenode(sz);
				fl.move_prev(*node, itnext);

				if (union_with_next) {
					node->sz += itnext->sz;
					freelist::unbind(*itnext);
					return;
				}
			}

			inline void engage_block(gxx::buffer buf) {
				engage_block(buf.data(), buf.size());
			}

			void* allocate(size_t sz) {
				size_t addsize = sz + sizeof(size_t);
				size_t realsize = addsize < sizeof(freenode) ? sizeof(freenode) : addsize;

				for(auto& f : fl) {
					if (f.sz >= realsize) {
						if (f.sz - realsize < sizeof(freenode)) {
							void* ptr = f.start();
							size_t sz = f.sz;
							freelist::unbind(f);
							*(size_t*)&f = sz;
							return ptr;
						} 
						else {
							dlist_head* next = f.lnk.next;
							dlist_head* prev = f.lnk.prev; 
							void* ptr = f.start();
							size_t sz = realsize;
							*(size_t*)&f = sz;
							freenode* node = new (reinterpret_cast<char*>(&f) + realsize) freenode(f.sz - realsize);
							__dlist_add(&node->lnk, next, prev);
							return ptr;
						}
					}
				}
				//dprln("null");

				return nullptr;
			}

			void deallocate(void* ptr) {
				size_t* rptr = ((size_t*) ptr) - 1; 
				size_t sz = *rptr;
				engage_block(rptr, sz);
			} 
		};
	}

	template<>
	struct print_functions<memory::heap> {
		static int print(gxx::io::ostream& o, memory::heap const& heap) {
		//	return gxx::fprint("({},{})", &node, node.sz);			
			for(auto& node : heap.fl) {
				gxx::fprintln(o, "{}, {}", &node, node.sz);
			}
		}
	};
}

#endif