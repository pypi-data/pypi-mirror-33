#ifndef GXX_GEN_H
#define GXX_GEN_H

/*#include <iterator>

namespace gxx {

	template<typename T, typename C>
	class gen {
		C& ctr;

	public:
		bool m_nil;
		gen(C& ctr, bool nil = false) : ctr(ctr), m_nil(nil) {}
		
		gen& operator++() {
			m_nil = ctr.next();
			return *this;
		}

		bool operator!=(gen& other) {
			return m_nil != other.m_nil; 
		}

		T& operator* () {
			return ctr.value();
		} 
	};
}

namespace std {
	template<typename T, typename C>
	class iterator_traits<gxx::gen<T,C>> {
	public:
		using iterator_category = std::forward_iterator_tag;
        using value_type = T;
	};
}*/

#endif
