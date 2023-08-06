#ifndef GXX_CONTAINER_H
#define GXX_CONTAINER_H

#include <map>
#include <gxx/generator.h>
#include <gxx/util/freeze.h>

namespace gxx { 
	namespace gen {
		class range : public gxx::generator<int, range> {
			int start;
			int stop;
		
		public:
			using value_type = int;

			range(int start, int stop) : start(start), stop(stop) {
				if (start == stop) nil();
			}
		
			~range() {
			}

			bool next() {
				return ++start != stop;
			}
		
			int value() {
				return start;
			}
		};
		
		template<typename C, typename R, typename F>
		class mapping_t : public gxx::generator<typename C::value_type, mapping_t<C,R,F>> {
			using type = typename C::value_type;
			gxx::freeze<R> sctr;
			typename C::const_iterator it;
			typename C::const_iterator eit;
			F f;

		public:
			using value_type = decltype(f(*it));

			mapping_t(F&& f,C&& ctr) : sctr(std::forward<C>(ctr)), f(f), it(sctr->begin()), eit(sctr->end()) {}
			mapping_t(mapping_t&& oth) : sctr(oth.sctr), it(sctr->begin()), eit(sctr->end()), f(oth.f) {}
			mapping_t(const mapping_t& oth) : sctr(oth.sctr), it(sctr->begin()), eit(sctr->end()), f(oth.f) {}
		
			bool next() {
    			return ++it != eit;
			}
		
			decltype(auto) value() {
				return f(*it);
			}
		};
		
		template<typename C, typename F>
		mapping_t<C,C&&,F> mapping(F&& f, C&& ctr) {
			return mapping_t<C,C&&,F>(std::forward<F>(f), std::forward<C>(ctr));
		} 

		template<typename C, typename R, typename F>
		class filter_t : public gxx::generator<typename C::value_type, filter_t<C,R,F>> {
			using parent = gxx::generator<typename C::value_type, filter_t<C,R,F>>;
			using type = typename C::value_type;
			gxx::freeze<R> sctr;
			typename C::const_iterator it;
			typename C::const_iterator eit;
			F f;
		
		public:
			using value_type = typename C::value_type;
            
			filter_t(F&& f, C&& ctr) : f(f), sctr(std::forward<C>(ctr)), it(sctr->begin()), eit(sctr->end()) { if (!find_next()) parent::nil(); }
			filter_t(filter_t&& oth) : sctr(oth.sctr), it(sctr->begin()), eit(sctr->end()), f(oth.f) {}
			filter_t(const filter_t& oth) : sctr(oth.sctr), it(sctr->begin()), eit(sctr->end()), f(oth.f) {}

			bool find_next() {
				while (true) {
					if (it == eit) return false;
					if (f(*it)) return true;
					++it; 
				}
			}

			bool next() {
				++it;
				return find_next();
			}
		
			type value() {
				return *it;
			}
		};
		
		template<typename C, typename F>
		filter_t<C,C&&,F> filter(F&& f, C&& ctr) {
			return filter_t<C,C&&,F>(std::forward<F>(f), std::forward<C>(ctr));
		}

		template<typename K, typename T>
        class keys_of_map_t : public gxx::generator<K, keys_of_map_t<K,T>> {
			typename std::map<K,T>::iterator it;
			typename std::map<K,T>::iterator eit;
	
		public:
            using value_type = K;
            using size_type = typename std::map<K,T>::size_type;

            keys_of_map_t(std::map<K,T>& dict) : it(dict.begin()), eit(dict.end()) {
                if (dict.empty()) keys_of_map_t<K,T>::nil();
			}
		
            K value() {
				return const_cast<K&>(it->first);
			}
		
			bool next() {
                return ++it != eit;
			}	
		};

        template<typename K, typename T>
        keys_of_map_t<K,T> keys_of_map(std::map<K,T>& ctr) {
            return keys_of_map_t<K,T>(ctr);
        }
 
	}

	namespace container {
        template <typename C>
		bool contain(const C& ctr, const typename C::value_type& pattern) {
			using type = typename C::value_type;
			for (const auto& a : ctr) {
				if (a == pattern) return true;
			}
			return false;
		}
	}
}

#endif // GXX_CONTAINER_H
