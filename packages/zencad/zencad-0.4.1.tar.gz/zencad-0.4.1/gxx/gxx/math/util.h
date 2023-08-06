#ifndef GXX_MATH_UTIL_H
#define GXX_MATH_UTIL_H

#include <cmath>

namespace gxx { namespace math {

	inline float veryquick_rsqrt( float number ) {
		long i;
		float x2, y;
		const float threehalfs = 1.5F;
	
		x2 = number * 0.5F;
		y  = number;
		i  = * ( long * ) &y;                       // evil floating point bit level hacking
		//i  = 0x5f3759df - ( i >> 1 );               // what the fuck? 
		i  = 0x5F375A86 - ( i >> 1 );               // what the fuck? 
		y  = * ( float * ) &i;
		y  = y * ( threehalfs - ( x2 * y * y ) );   // 1st iteration
	//	y  = y * ( threehalfs - ( x2 * y * y ) );   // 2nd iteration, this can be removed
	
		return y;
	}
	
	inline float quick_rsqrt( float number ) {
		long i;
		float x2, y;
		const float threehalfs = 1.5F;
	
		x2 = number * 0.5F;
		y  = number;
		i  = * ( long * ) &y;                       // evil floating point bit level hacking
		//i  = 0x5f3759df - ( i >> 1 );               // what the fuck? 
		i  = 0x5F375A86 - ( i >> 1 );               // what the fuck? 
		y  = * ( float * ) &i;
		y  = y * ( threehalfs - ( x2 * y * y ) );   // 1st iteration
		y  = y * ( threehalfs - ( x2 * y * y ) );   // 2nd iteration, this can be removed
	
		return y;
	}

	template <typename T, T prec>
	static inline bool is_same_template(T a, T b) {
		return fabs(a-b) < prec;
	}

	template <typename T, typename P>
	static inline bool is_same(T a, T b, P prec) {
		return fabs(a-b) < prec;
	}

	template <typename T, typename P>
	static inline bool early_zero(T a, P prec) {
		return fabs(a) < prec;
	}


	static inline double rad2angle(double r) {
		return r / 2 / M_PI * 360;
	}

	template<typename T> T maximum(T a, T b) { return a > b ? a : b; }
	template<typename T> T minimum(T a, T b) { return a < b ? a : b; }

	template<typename T>
	T limitation(const T& a, const T& min, const T& max) {
		return min > a ? min : max < a ? max : a;
	}

	inline double degree(double arg) {
		return arg * M_PI / 180;
	}
}}
#endif