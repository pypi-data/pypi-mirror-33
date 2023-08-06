#ifndef GXX_SLICE_H
#define GXX_SLICE_H

#include <gxx/print.h>
#include <inttypes.h>
#include <stdlib.h>
#include <gxx/util/setget.h>

namespace gxx {
	template <typename T>
	class object_buffer {
	protected:
		T* m_data;
		size_t m_size;

	public:
		ACCESSOR(data, m_data);
		ACCESSOR(size, m_size);
		
		VALUE_GETTER(bytesize, m_size * sizeof(T));

		object_buffer() : m_data(nullptr), m_size(0) {};
		object_buffer(const T* data, size_t size) : m_data((T*)data), m_size(size) {}

		template<size_t N>
		object_buffer(const T (& data) [N]) : m_data((T*) data), m_size(N) {}

		//object_buffer(const T (& data) [N]) : m_data((T*) data), m_size(N) {}


		using iterator = T*;
		using const_iterator = const T*;

		iterator begin() {
			return m_data;
		}

		const iterator end() {
			return m_data + m_size;
		}

		const_iterator begin() const {
			return m_data;
		}

		const const_iterator end() const {
			return m_data + m_size;
		}

		gxx::object_buffer<T> slice(){
			return gxx::object_buffer<T>(m_data, m_size);
		}

		gxx::object_buffer<T> slice(size_t len){
			return gxx::object_buffer<T>(m_data, len);
		}

		gxx::object_buffer<T> slice(size_t first, size_t len){
			return gxx::object_buffer<T>(m_data + first, len);
		}
	
		T& operator[](int i) {
			return *(m_data + i);
		}

		const T& operator[](int i) const {
			return *(m_data + i);
		}

		bool operator==(const object_buffer& other) const {
			if (m_size != other.m_size) return false;
			for(int i = 0; i < m_size; i++) {
				if (m_data[i] != other.m_data[i]) return false;
			}
			return true;
		}

		size_t printTo(gxx::io::ostream& o) const {
			o.putchar('[');
			for(int i = 0; i < m_size; ++i) {
				gxx::print(*(m_data + i));
				if (i != m_size - 1) o.putchar(' ');
			}
			o.putchar(']');
		}

		//template<typename M>
		//void serialize(M& m) {
		//	m & gxx::buffer(m_data, sizeof(T) * sz);
		//}

		//template<typename M>
		//void deserialize(M& m) {
			///m & gxx::buffer(m_data, sizeof(T) * sz);
		//}
	};

	template<typename T>
	using objbuf = object_buffer<T>;


	template<typename T>
	objbuf<T> make_objbuf(T* data, size_t sz) {
		return objbuf<T>(data, sz);
	}

/*	template <typename T, typename Allocator = gxx::allocator<T>>
	class allocated_object_buffer : public object_buffer<T> {
		using Parent = object_buffer<T>;

		Allocator m_alloc;
	public:
		CONSTREF_GETTER(data, Parent::m_data);
		CONSTREF_GETTER(size, Parent::m_size);

		allocated_object_buffer(size_t n) : object_buffer<T>(m_alloc.allocate(n), n) {}

		~allocated_object_buffer() {
			m_alloc.deallocate(Parent::m_data);
		}
	};*/
}

#endif