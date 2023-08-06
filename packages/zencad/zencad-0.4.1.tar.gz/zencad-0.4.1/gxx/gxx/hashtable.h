#ifndef GXX_HASHTABLE_H
#define GXX_HASHTABLE_H

#include <gxx/util/member.h>
#include <gxx/util/hash.h>
#include <gxx/util/compare.h>
#include <gxx/datastruct/hlist_head.h>
#include <gxx/datastruct/array.h>

namespace gxx {

	template <size_t TableSize, typename T, typename K, hlist_node T::* lnk, 
		K&(*GetKey)(T&) = T::getkey> 
	class static_hashtable {
		hlist_head table[TableSize];

	public:
		static_hashtable() {
			for (auto& t: table) hlist_head_init(&t);
		}	

		void put(T& item) {
			hlist_node* node = &(item.*lnk);
			K& key = GetKey(item);
			size_t hash = gxx::hash(key);
			__hashtable_put_to_cell(table, node, hash % TableSize);
		}
		
		T* get(const K& key) {
			size_t hash = gxx::hash(key);	
			struct hlist_node* pos;

			hlist_for_each(pos, table + hash % TableSize) {
				if (gxx::equal(GetKey(*member_container(pos, lnk)), key)) 
					return member_container(pos, lnk);
			}
			return nullptr;
		}

		void dump() {
			for (int i = 0; i < TableSize; i++) {
				int n = 0;
				struct hlist_node * curnode;
				hlist_for_each(curnode, (table + i)) {
					n++;
				}
			}
		}

		template <typename Function>
		void foreach(Function func) {
			for (auto& t: table) {
				struct hlist_node * pos;
				hlist_for_each(pos, &t) {
					func(*member_container(pos, lnk));
				}
			}
		}

		template <typename Function>
		T* find(Function func) {
			for (auto& t: table) {
				struct hlist_node * pos;
				hlist_for_each(pos, &t) {
					T& el = *member_container(pos, lnk);
					if (func(el)) return &el;
				}
			}
			return nullptr;
		}

	private:

		void __hashtable_put_to_cell(struct hlist_head* tbl, struct hlist_node* node, size_t cell) {
			struct hlist_head* hcell = tbl + cell;
			hlist_add_next(node, &hcell->first);
		}
	};
}

#endif
