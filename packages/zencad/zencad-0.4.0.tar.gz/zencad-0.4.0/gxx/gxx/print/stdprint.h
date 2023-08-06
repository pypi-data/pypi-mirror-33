#ifndef GXX_STD_PRINT_H
#define GXX_STD_PRINT_H

#include <gxx/print.h>
#include <gxx/container/dlist.h>

#include <array>
#include <vector>
#include <map>
#include <set>
#include <list>

//#include <typeinfo>

namespace gxx {
	template<typename T>
	size_t print_array_like_to(gxx::io::ostream& o, const T& arr) {
		o.putchar('[');
		int s = arr.size();
		for (const auto& g : arr) {
			gxx::print_to(o, g);
			if (--s) o.putchar(',');
		}
		o.putchar(']');
	}

	template<typename T, typename A> 
	struct print_functions<std::vector<T,A>> {
		static int print(gxx::io::ostream& o, std::vector<T,A> const& vec) {
			return print_array_like_to(o, vec);
		}
	};

	template<typename T, typename A> 
	struct print_functions<std::set<T,A>> {
		static int print(gxx::io::ostream& o, std::set<T,A> const& vec) {
			return print_array_like_to(o, vec);			
		}
	};

	template<typename T, typename A> 
	struct print_functions<std::list<T,A>> {
		static int print(gxx::io::ostream& o, std::list<T,A> const& vec) {
			return print_array_like_to(o, vec);
		}
	};

	template<typename T, dlist_head T::* L> 
	struct print_functions<gxx::dlist<T,L>> {
		static int print(gxx::io::ostream& o, gxx::dlist<T,L> const& vec) {
			return print_array_like_to(o, vec);
		}
	};

	template<typename T, size_t N> 
	struct print_functions<std::array<T,N>> {
		static int print(gxx::io::ostream& o, std::array<T,N> const& vec) {
			return print_array_like_to(o, vec);
		}		
	};

	//template<typename T> 
	//struct print_functions<std::set<T>> {
	//	static int print(gxx::io::ostream& o, std::set<T> const& vec) {
	//		return print_array_like_to(o, vec);
	//	}		
	//};

	template<typename T, typename K>  
	struct print_functions<std::map<K,T>> {
		static int print(gxx::io::ostream& o, std::map<K,T> const& dict) {
			o.putchar('{');
			if (dict.size() != 0) {
				auto it = dict.begin();
				auto end = dict.end();

				gxx::print_to(o, (*it).first); o.putchar(':'); gxx::print_to(o, (*it).second);
				it++;
				while(it != end) {
					o.putchar(',');
					gxx::print_to(o, (*it).first); o.putchar(':'); gxx::print_to(o, (*it).second);	
					it++;
				}
			} 
			o.putchar('}');
		}
	};

	template<> 
	struct print_functions<std::string> {
		static int print(gxx::io::ostream& o, const std::string& str) {
			return o.print(str.c_str());
		}
	};

	template<typename T0, typename T1>  
	struct print_functions<std::pair<T0,T1>> {
		static int print(gxx::io::ostream& o, std::pair<T0,T1> const& pr) {
			o.putchar('(');
			gxx::print_to(o, pr.first);
			o.putchar(',');
			gxx::print_to(o, pr.second);
			o.putchar(')');
		}
	};

	/*template<>
	struct print_functions<std::type_info> {
		static int print(gxx::io::ostream& o, std::type_info const& info) {
			return gxx::print_to(o, info.name());
		}
	};*/
}


#endif
