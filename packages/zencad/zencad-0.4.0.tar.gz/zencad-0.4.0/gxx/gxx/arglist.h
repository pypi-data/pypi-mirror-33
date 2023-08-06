#ifndef GXX_ARGLIST2_H
#define GXX_ARGLIST2_H

//Структура данных visitable_arglist используется для форматирующей печати.
//Для обработки строки формата все аргументы однотипно записываются с помощью указателей,
//указатели их обработчиков также сохраняются, тем самым осуществляя сохранение типа.
//За подбор обработчиков отвечает класс визитёр (Visitor). Он же ответственен за вызов.
//Таким образом visitable_arglist - это средство разграничения во времени многоаргументного
//вызова и его исполнения.

#include <memory>
#include <utility>
#include <assert.h>
#include <gxx/buffer.h>
#include <gxx/panic.h>

namespace gxx {
	template <typename T> class argpair;
	struct argname {
		gxx::buffer name;
		argname(const gxx::buffer& _name) : name(_name) {};

		template<typename T>
		constexpr argpair<typename std::remove_reference<T>::type> operator= (T&& body) {
			return argpair<typename std::remove_reference<T>::type>(name, (void*)&body);
		}
	};

	template<typename T>
	struct argpair {
		using type = T;

		void* body;
		gxx::buffer name;

		constexpr argpair(const gxx::buffer& _name, void* _body) : body(_body), name(_name) {}
	};

	namespace argument_literal {
		static argname operator"" _a (const char* name, size_t sz) {
			return argname(gxx::buffer(name, sz));
		}
	}

	struct visitable_argument {
		void* 		ptr;
		void* 		visit;
		gxx::buffer name;

		visitable_argument(){}
		visitable_argument(void* _ptr, void* _visit, const gxx::buffer& buf) : ptr(_ptr), visit(_visit), name(buf) {}
	};

	template<typename HT, typename ... Tail>
	static inline void visitable_arglist_former(visitable_argument* argptr, const HT& head, const Tail& ... tail) {
		new (argptr) visitable_argument( head );
		visitable_arglist_former(++argptr, tail ...);
	}

	static inline void visitable_arglist_former(visitable_argument* argptr) {
		(void) argptr;
	}

	class visitable_arglist {
	public:
		size_t N;
		visitable_argument* arr;

		template <typename ... Args>
		visitable_arglist(visitable_argument* buffer, Args&& ... args) : arr(buffer), N(sizeof ... (Args)) {
			visitable_arglist_former(arr, args ...);
		}

		visitable_arglist() : N(0), arr(nullptr) {}

		visitable_argument* begin() {
			return arr;
		}

		visitable_argument* end() {
			return arr + N;
		}

		const visitable_argument& operator[](size_t num) const {
			assert(num < N);
			return arr[num];
		}

		const visitable_argument& operator[](gxx::buffer str) const {
			for(uint8_t i = 0; i < N; ++i) {
				if (str == arr[i].name) return arr[i];
			}
			gxx::panic("visitable_arglist: name error");
			return arr[0]; // -Wreturn-type
		}
	};

	template <typename Visitor, typename Object>
	inline visitable_argument make_visitable_argument(Object& obj) {
		return visitable_argument((void*)&obj, Visitor::template get_visit<typename std::remove_const<typename std::remove_reference<Object>::type>::type>(), gxx::buffer());
	}

	template <typename Visitor, typename Object, size_t N>
	inline visitable_argument make_visitable_argument(Object(&obj)[N]) {
		return visitable_argument((void*)obj, Visitor::template get_visit<typename std::remove_const<typename std::remove_reference<Object>::type>::type*>(), gxx::buffer());
	}

	template <typename Visitor, typename Object>
	inline visitable_argument make_visitable_argument(Object*& obj) {
		return visitable_argument((void*)obj, Visitor::template get_visit<typename std::remove_const<typename std::remove_reference<Object>::type>::type*>(), gxx::buffer());
	}

	template <typename Visitor, typename Object>
	inline visitable_argument make_visitable_argument(argpair<Object>& pair) {
		return visitable_argument(pair.body, Visitor::template get_visit<typename std::remove_const<typename std::remove_reference<Object>::type>::type>(), pair.name);
	}

	template <typename Visitor, typename Object, size_t N>
	inline visitable_argument make_visitable_argument(argpair<Object[N]>& pair) {
		return visitable_argument(pair.body, Visitor::template get_visit<typename std::remove_const<typename std::remove_reference<Object>::type>::type*>(), pair.name);
	}

	template <typename Visitor, typename Object>
	inline visitable_argument make_visitable_argument(argpair<Object*>& pair) {
		return visitable_argument(*(void**)pair.body, Visitor::template get_visit<typename std::remove_const<typename std::remove_reference<Object>::type>::type*>(), pair.name);
	}

	template <typename Visitor, typename ... Args>
	inline visitable_arglist make_visitable_arglist(visitable_argument* buffer, Args&& ... args) {
		return visitable_arglist(buffer, make_visitable_argument<Visitor>(args) ...);
	}
}

#endif
