#ifndef GXX_ARGSLIST_H
#define GXX_ARGSLIST_H

#include <utility>

#include <string.h>
#include <gxx/buffer.h>
//#include <gxx/debug/type_analize.h>

namespace gxx {	

	template <typename T> class argpair; 

	struct argname {
		const char*& name;
		argname(const char*& name) : name(name) {}; 
		
		template<typename T> 
		constexpr argpair<T> operator= (T&& body) { 
			return argpair<T>(name, body);
		}
	};
	
	template<typename T>
	struct argpair {
		T body;
		const char* name;

		template<typename U>
		constexpr argpair(const char* name, U&& body) : body(body), name(name) { 
			//pretty_that_function(); 
		}
	};

	template<typename T, typename F>
	class argument_temporary {
	public:
		T arg;
		const char* name;
		
		template<typename U>
		argument_temporary(U&& arg, const char* name = nullptr) : arg(std::forward<U>(arg)), name(name) {
			//pretty_that_function();dprln();
		}
	};

	template<typename T>
	argument_temporary<T, const T> make_argument_temporary(T&& arg) {
		//pretty_that_function();dprln();
		return argument_temporary<T, const T>(std::forward<T>(arg));
	} 

	template<typename T>
	argument_temporary<T&, const T> make_argument_temporary(T& arg) {
		//pretty_that_function();dprln();
		return argument_temporary<T&, const T>(arg);
	}

	template<typename T>
	argument_temporary<T*, const T* const> make_argument_temporary(T*& arg) {
		//pretty_that_function();dprln();
		return argument_temporary<T*, const T* const>(arg);
	}

	template<typename T, size_t N>
	argument_temporary<T*, const T* const> make_argument_temporary(T(&arg)[N]) {
		//pretty_that_function();dprln();
		return argument_temporary<T*, const T* const>(arg);
	} 

	template<typename T>
	argument_temporary<T, const T> make_argument_temporary(argpair<T>&& arg) {
		//pretty_that_function();dprln();
		return argument_temporary<T, const T>(arg.body, arg.name);
	} 

	template<typename T>
	argument_temporary<T&, const T> make_argument_temporary(argpair<T&>&& arg) {
		//pretty_that_function();dprln();
		return argument_temporary<T&, const T>(arg.body, arg.name);
	} 

	template<typename T>
	argument_temporary<T*, const T* const> make_argument_temporary(argpair<T*&>&& arg) {
		//pretty_that_function();dprln();
		return argument_temporary<T*, const T* const>(arg.body, arg.name);
	} 

	template<typename T, size_t N>
	argument_temporary<const T*, const T* const> make_argument_temporary(argpair<T(&)[N]>&& arg) {
		//pretty_that_function();dprln();
		return argument_temporary<const T*, const T* const>(arg.body, arg.name);
	}
	

	namespace argument_literal {
		static argname operator"" _a (const char* name, size_t sz) { 
			(void) sz; 
			return argname(name); 
		} 
	}

	struct argument {
		void* ptr;
		void* func; 
		const char* name; 

	public:
		argument(){};

		argument(void* ptr, void* func, const char* name = nullptr) : ptr(ptr), func(func), name(name) {}

		//template <typename T>
		//argument(argpair<T>& pair, void* func) : ptr((void*)&pair.body), name(pair.name), func(func) {}
	};

	template<typename HT, typename ... Tail>
	static inline void arglist_former(argument* argptr, const HT& head, const Tail& ... tail) {
		new (argptr) argument( head );
		arglist_former(++argptr, tail ...);
	}

	static inline void arglist_former(argument* argptr) {
		(void) argptr;
	}
	
	class arglist {
	public:
		argument list[15];
		size_t listsz;
	
		template<typename ... UArgs>
		explicit arglist(UArgs&& ... args) {
			arglist_former(list, std::forward<UArgs>(args) ...);
			listsz = sizeof...(args);
		}
		const argument& operator[](int i) const;

		argument* begin();
		argument* end();

		int find_name(const char* name, size_t len) const;
	};

	template<typename Customer, typename T, typename F>
	argument make_argument(argument_temporary<T, F>&& arg) { 
		//pretty_that_function();dprln();
		return argument((void*)&arg.arg, (void*) Customer::template function_pointer<F>(), arg.name); 
	}

	/*template<typename Formatter, typename ... Args>
	arglist make_arglist(Args ... args) { 
		return arglist(gxx::make_argument<Formatter>(gxx::make_argument_temporary(std::forward<Args>(args))) ...); 
	}*/

	/*template<typename Customer, typename T, typename F>
	argument make_argument(argument_temporary<T&, F>&& arg) { 
		//pretty_that_function();dprln();
		return argument((void*)&arg.arg, (void*) Customer::template function_pointer<F>(), arg.name); 
	}*/

	/*template<typename Customer, typename T>
	argument make_argument(argument_temporary<T&>&& arg) { 
		pretty_that_function();dprln();
		return argument((void*)&arg, (void*) Customer::template function_pointer<T>()); 
	}*/
}

#endif