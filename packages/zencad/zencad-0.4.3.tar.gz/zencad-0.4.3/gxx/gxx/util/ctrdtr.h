#ifndef GXX_UTIL_CTR_DTR_H
#define GXX_UTIL_CTR_DTR_H

//#include <gxx/util/placed_new.h>

namespace gxx {
	template<typename T>
	void destructor(T* ptr) {
		ptr->~T();
	}
	
	template<class InputIterator>  
	void
	array_destructor(InputIterator first, InputIterator last)
	{
		while(first != last){
			gxx::destructor(&*first);
			++first;
		}
	}
	
	template<typename T, typename ... Args>
	void constructor(T* ptr, Args&& ... args) {
		new(ptr) T(std::forward<Args>(args)...);
	}
	
	template<typename T>
	void copyConstructor(T* ptr, const T& other) {
		new(ptr) T(other);
	}
	
	template<typename T>
	void moveConstructor(T* ptr, T&& other) {
		new(ptr) T(std::forward<T>(other));
	}
	
	template<class InputIterator, typename ... Args>  
	void
	array_constructor(InputIterator first, InputIterator last, Args ... args) {
		while(first != last){
			gxx::constructor(&*first, args ...);
			++first;
		}
	}

}

#endif