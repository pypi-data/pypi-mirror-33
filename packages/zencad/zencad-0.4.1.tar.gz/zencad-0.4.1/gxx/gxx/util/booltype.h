#ifndef GXX_UTIL_BOOLTYPE_H
#define GXX_UTIL_BOOLTYPE_H

namespace gxx {
	template<class T, T v>
	struct integral_constant {
	    static constexpr T value = v;
	    typedef T value_type;
	    typedef integral_constant type; // using injected-class-name
	    constexpr operator value_type() const noexcept { return value; }
	    constexpr value_type operator()() const noexcept { return value; } //since c++14
	};
	
	using true_type = gxx::integral_constant<bool, true>;
	using false_type = gxx::integral_constant<bool, false>;
}

#endif