#ifndef GXX_GENERATOR_H
#define GXX_GENERATOR_H

#include <vector>

namespace gxx {
	template<typename T, typename C>
	class generator {
	public:
		using iterator = C&;
		using const_iterator = C&;

		C& operator++() {
			((C*)this)->next();			
			return *(C*)this;
		}

		decltype(auto) operator* () {
			return ((C*)this)->value();
		} 	

		C& begin() const { return *(C*)this; }
		C& end() const { return *(C*)this; }

		bool operator != (generator& et) {
			return ((C*)this)->have();
		}

		bool operator == (generator& et) {
			return !((C*)this)->have();
		}

		operator std::vector<T>() {
			std::vector<T> vec;
			for (const auto& t: *this) vec.emplace_back(t);
			return vec;
		}
	};
}

namespace std {
	template<typename T, typename C>
	class iterator_traits<gxx::generator<T,C>> {
	public:
		using iterator_category = std::forward_iterator_tag;
		using value_type = T;
	};
}

#endif
