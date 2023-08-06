#ifndef GXX_CONCEPT_H
#define GXX_CONCEPT_H

namespace gxx {
	namespace concept {
		template<template <class> class C, class T>
		class sequence_container {
		public:
			const C<T>& container;
			sequence_container(const C<T>& c) : container(c) {}
			//sequence_container(const std::initializer_list<T>& c) : container(c) {}

			CONSTREF_GETTER(size, container.size());
		};
	}
}

#endif