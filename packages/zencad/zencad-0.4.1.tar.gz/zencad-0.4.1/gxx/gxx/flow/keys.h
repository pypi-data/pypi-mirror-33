#ifndef GXX_FLOW_KEYS_H
#define GXX_FLOW_KEYS_H

#include <gxx/generator.h>

namespace gxx {
	namespace flow {
		template <typename C>
		class keys_fn : public gxx::generator<typename C::value_type, keys_fn<C>> {
			const C& c;
			
			decltype(c.begin()) it;
			decltype(c.end()) eit;			
		public:
			using value_type = typename C::value_type;
			using reference = typename C::reference;
			using const_reference = typename C::const_reference;

			keys_fn(const C& c) : c(c), it(c.begin()), eit(c.end()) {}
		
			decltype(auto) value() {
				return it->first;
			}

			void next() {
				++it; 
			}

			bool have() {
				return it != eit;
			}
		};

		//struct keys {};

		template <typename C>
		keys_fn<C> keys (const C& c) {
			return keys_fn<C>(c);
		}
	}
}

#endif