#ifndef GXX_FREEZE_H
#define GXX_FREEZE_H

//TODO

#include <utility>
#include <gxx/print.h>

namespace gxx {
	template <typename T> class freeze;

	template <typename T> class freeze<T&> {
	public:
		T& ref;
		freeze(const T& ref) : ref(ref) {}
		freeze(const freeze& c) : ref(c.ref) {}
		auto operator->() { return &ref; }
	};

	template <typename T> class freeze<T&&> {
	public:
		T ref;
		freeze(T&& ref) : ref(std::move(ref)) {}
		freeze(const freeze& c) : ref(c.ref) {}
		auto operator->() { return &ref; }
	};
}

#endif