#ifndef GXX_VIEW_MAP_H
#define GXX_VIEW_MAP_H

#include <gxx/generator.h>
//#include <gxx/util/signature.h>

namespace gxx {
	namespace flow {
		template <typename F, typename C>
		class map_view : public gxx::generator<typename C::value_type, map_view<F,C>> {
			const C& c;
			const F& f;

			decltype(c.begin()) it;
			decltype(c.end()) eit;			
		public:
			using value_type = typename C::value_type;
			using reference = typename C::reference;
			using const_reference = typename C::const_reference;

			map_view(const F& f, const C& c) : f(f), c(c), it(c.begin()), eit(c.end()) {}
		
			typename C::value_type value() {
				return f(*it);
			}

			void next() {
				++it; 
			}

			bool have() {
				return it != eit;
			}
		};

		template <typename F>
		struct map_fabric_view {
			const F& f;
			map_fabric_view(const F& f) : f(f) {};			
		};

		template <typename F>
		auto map(const F& f) {
			return map_fabric_view<F>(f);
		}

		template <typename F, typename C>
		auto operator | (const C& c, const map_fabric_view<F>& fabric) {
			return map_view<F,C>(fabric.f, c);
		}		
	}
}

#endif