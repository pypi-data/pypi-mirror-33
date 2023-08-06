#ifndef GXX_VIEW_FOREACH_H
#define GXX_VIEW_FOREACH_H

#include <gxx/generator.h>
//#include <gxx/util/signature.h>

namespace gxx {
	namespace flow {
		template <typename F>
		struct foreach_cooler {
			const F& f;
			foreach_cooler(const F& f) : f(f) {}
		};

		template <typename F>
		auto foreach(const F& f) {
			return foreach_cooler<F>(f);
		}

		template <typename F, typename C>
		static inline void operator | (const C& c, const foreach_cooler<F>& cooler) {
			auto it = c.begin();
			auto eit = c.end();
			while (it != eit) {
				cooler.f(*it);
				++it;
			}
		}
		
	}
}

#endif