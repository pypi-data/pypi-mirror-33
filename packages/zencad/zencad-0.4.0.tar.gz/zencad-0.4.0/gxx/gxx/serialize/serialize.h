#ifndef GXX__SERIALIZESERIALIZE_H
#define GXX__SERIALIZESERIALIZE_H

#include <gxx/util/stub.h>
#include <gxx/result.h>
#include <gxx/buffer.h>
#include <tuple>
#include <vector>
#include <sstream>

namespace gxx {
	template <typename M, typename T, typename U = int>
	struct is_have_serialize : std::false_type { };

	template <typename M, typename T>
	struct is_have_serialize <M, T, decltype((void) &T::template serialize<M>, 0)> : std::true_type { };

	template <typename M, typename T, bool HaveSerialize = true>
	struct serialize_helper_basic {
		static void serialize(M& keeper, const T& obj) {
			obj.serialize(keeper);
		}

		static void deserialize(M& keeper, T& obj) {
			obj.deserialize(keeper);
		}
	};

	template <typename M, typename T>
	struct serialize_helper_basic<M,T,false> {
		static void serialize(M& keeper, const T& obj) {
			keeper.dump(obj);
		}

		static void deserialize(M& keeper, T& obj) {
			keeper.load(obj);
		}

		static void deserialize(M& keeper, T&& obj) {
			keeper.load(obj);
		}
	};

	template <typename M, typename T>
	struct serialize_helper : public serialize_helper_basic<M,T,is_have_serialize<M,T>::value> {};

	template <typename M, typename T> inline void serialize(M& keeper, const T& obj) {
		serialize_helper<M,T>::serialize(keeper, obj);
	}

	template <typename M, typename T> inline void deserialize(M& keeper, T& obj) {
		serialize_helper<M,std::remove_cv_t<T>>::deserialize(keeper, obj);
	}

	//template <typename M, typename T> inline void serialize(M& keeper, T&& obj) {
	//	serialize_helper<M,std::remove_cv_t<T>>::serialize(keeper, std::move(obj));
	//}

	template <typename M, typename T> inline void deserialize(M& keeper, T&& obj) {
		serialize_helper<M,std::remove_cv_t<T>>::deserialize(keeper, std::move(obj));
	}

	namespace archive {

		template <typename T>
		struct data {
			T* ptr;
			size_t sz;
			data(T* ptr, size_t sz) : ptr(ptr), sz(sz) {}
			data(const T* ptr, size_t sz) : ptr((T*)ptr), sz(sz) {}
			template<typename R> void reflect(R& r) { r.do_data((char*)ptr, sz * sizeof(T)); }
		};

		/*template <typename T, typename S, typename A = std::allocator<T>>
		struct allocated_data {
			T*& ptr;
			S& sz;
			A alloc;
			allocated_data(T*& ptr, S& sz, const A& alloc) : ptr(&ptr), sz(sz), alloc(alloc) {}

			template<typename R>
			void serialize(R& r) const {
				r.dump(sz);
				r.dump_data(ptr, sz * sizeof(T));
			}

			template<typename R>
			void deserialize(R& r) {
				r.load(sz);
				ptr = alloc.allocate(sz);
				r.dump_data(ptr, sz * sizeof(T));
			}
		};*/

		class binary_serializer_basic {
		public:
			template<typename T>
			void operator& (const T& obj) {
				gxx::serialize(*this, obj);
			}

			virtual void dump_data(const char* dat, uint16_t sz) = 0;
			void do_data(const char* dat, uint16_t sz) { dump_data(dat, sz); }

			void dump(const char* dat, uint16_t sz) {
				dump(sz);
				dump_data(dat, sz);
			}

			void dump(char i) { dump_data((char*)&i, sizeof(i)); }
			void dump(short i) { dump_data((char*)&i, sizeof(i)); }
			void dump(int i) { dump_data((char*)&i, sizeof(i)); }
			void dump(long i) { dump_data((char*)&i, sizeof(i)); }
			void dump(unsigned char i) { dump_data((char*)&i, sizeof(i)); }
			void dump(unsigned short i) { dump_data((char*)&i, sizeof(i)); }
			void dump(unsigned int i) { dump_data((char*)&i, sizeof(i)); }
			void dump(unsigned long i) { dump_data((char*)&i, sizeof(i)); }
                        void dump(unsigned long long i) { dump_data((char*)&i, sizeof(i)); }
			void dump(float i) { dump_data((char*)&i, sizeof(i)); }
			void dump(double i) { dump_data((char*)&i, sizeof(i)); }
			void dump(long double i) { dump_data((char*)&i, sizeof(i)); }

			template<typename T>
			void dump(const T& ref) {
				((std::remove_cv_t<std::remove_reference_t<T>>&)(ref)).reflect(*this);
			}
		};

		class binary_string_writer : public binary_serializer_basic {
		public:
			std::string& sstr;

			void dump_data(const char* dat, uint16_t size) override {
				sstr.append(dat, size);
			}

			binary_string_writer(std::string& str) : sstr(str) {}
		};

		class binary_deserializer_basic {
		public:
			template<typename T>
			void operator& (T&& obj) {
				gxx::deserialize(*this, obj);
			}

			virtual void load_data(char* dat, uint16_t sz) = 0;
			void do_data(char* dat, uint16_t sz) { load_data(dat, sz); }

			void load(char* dat, uint16_t maxsz) {
				uint16_t sz;
				load(sz);
				assert(sz <= maxsz);
				load_data(dat, sz);
			}

			void load(char& i) { load_data((char*)&i, sizeof(i)); }
			void load(short& i) { load_data((char*)&i, sizeof(i)); }
			void load(int& i) { load_data((char*)&i, sizeof(i)); }
			void load(long& i) { load_data((char*)&i, sizeof(i)); }
			void load(unsigned char& i) { load_data((char*)&i, sizeof(i)); }
			void load(unsigned short& i) { load_data((char*)&i, sizeof(i)); }
			void load(unsigned int& i) { load_data((char*)&i, sizeof(i)); }
			void load(unsigned long& i) { load_data((char*)&i, sizeof(i)); }
                        void load(unsigned long long& i) { load_data((char*)&i, sizeof(i)); }
			void load(float& i) { load_data((char*)&i, sizeof(i)); }
			void load(double& i) { load_data((char*)&i, sizeof(i)); }
			void load(long double& i) { load_data((char*)&i, sizeof(i)); }

			template<typename T>
			void load(T&& ref) {
				((std::remove_cv_t<std::remove_reference_t<T>>&)(ref)).reflect(*this);
			}
		};

		class binary_string_reader : public binary_deserializer_basic {
		public:
			std::istringstream stream;

			void load_data(char* dat, uint16_t size) override {
				stream.read(dat, size);
			}

			binary_string_reader(const std::string& str) : stream(str) {}
		};
	}




	template<typename Archive, typename ... Args>
	struct serialize_helper<Archive, std::tuple<Args...>> {
		using Tuple = std::tuple<Args...>;

		template<typename std::size_t ... I>
		static void tuple_serialize_helper(Archive& keeper, const Tuple& tpl, std::index_sequence<I...>) {
			int ___[] = {
				(gxx::serialize(keeper, std::get<I>(tpl)), 0) ...
			};
		}

		static void serialize(Archive& keeper, const Tuple& tpl) {
			tuple_serialize_helper(keeper, tpl, std::index_sequence_for<Args...>{});
		}

		template<typename std::size_t ... I>
		static void tuple_deserialize_helper(Archive& keeper, Tuple& tpl, std::index_sequence<I...>) {
			int ___[] = {
				(gxx::deserialize(keeper, std::get<I>(tpl)), 0) ...
			};
		}

		static void deserialize(Archive& keeper, Tuple& tpl) {
			tuple_deserialize_helper(keeper, tpl, std::index_sequence_for<Args...>{});
		}
	};

	template<typename Archive>
	struct serialize_helper<Archive, std::string> {
		static void serialize(Archive& keeper, const std::string& str) {
			gxx::serialize(keeper, gxx::buffer(str.data(), str.size()));
		}

		static void deserialize(Archive& keeper, std::string& str) {
			gxx::panic("todo");
		}
	};

	template<typename Archive, typename T>
	struct serialize_helper<Archive, std::vector<T>> {
		static void serialize(Archive& keeper, const std::vector<T>& vec) {
			gxx::serialize(keeper, vec.size());
			gxx::serialize(keeper, gxx::archive::data<T>{vec.data(), vec.size()});
		}

		static void deserialize(Archive& keeper, std::vector<T>& vec) {
			size_t sz;
			gxx::deserialize(keeper, sz);
			vec.resize(sz);
			gxx::deserialize(keeper, gxx::archive::data<T>{vec.data(), sz});
		}
	};
}

#endif
