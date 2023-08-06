#ifndef GXX_MAJOR_H
#define GXX_MAJOR_H

#include <stdlib.h>

namespace gxx {
	namespace math {
		class coord1_compact {};
		class coord2_compact {};

		using column_major = coord1_compact;
		using row_major = coord2_compact;

		template<typename S, typename O>
		struct major_accessor;
	
		template<typename S>
		struct major_accessor<S, coord1_compact> {
			static inline auto& ref(S& s, size_t i1, size_t i2, size_t s1, size_t s2) {
				return s[i2 * s1 + i1];
			}
			static inline const auto& const_ref(const S& s, size_t i1, size_t i2, size_t s1, size_t s2) {
				return s[i2 * s1 + i1];
			}
		};
	
		template<typename S>
		struct major_accessor<S, coord2_compact> {
			static inline auto& ref(S& s, size_t i1, size_t i2, size_t s1, size_t s2) {
				return s[i1 * s2 + i2];
			}
			static inline const auto& const_ref(const S& s, size_t i1, size_t i2, size_t s1, size_t s2) {
				return s[i1 * s2 + i2];
			}
		};
	}
}

#endif