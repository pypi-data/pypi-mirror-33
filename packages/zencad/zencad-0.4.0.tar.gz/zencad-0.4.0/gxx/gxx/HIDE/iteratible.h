#ifndef GXX_ITERATIBLE_H
#define GXX_ITERATIBLE_H

#include <gxx/gen.h>
#include <gxx/buffer.h>
#include <string.h>

/*namespace gxx {

	class range {
		int stop;
		int m_value;
	
		using iterator = gxx::gen<int, range>;
	
	public:
		range(int start, int stop) : m_value(start), stop(stop) {}
	
		int& value() {
			return m_value;
		}
	
		bool next() {
			m_value++;
			return m_value == stop;
		}	
	
		iterator begin() {
			return iterator(*this); 
		}
	
		iterator end() {
			return iterator(*this, true);
		}
	};

	class split_tokenizer {
		char* ptr;
		size_t room;
		gxx::buffer m_value;

		char delim;

		using iterator = gxx::gen<gxx::buffer, split_tokenizer>;
	
	public:
		split_tokenizer(const char* str, char dlm) : ptr((char*)str), room(strlen(str)), delim(dlm), m_value() {}
	
		gxx::buffer& value() {
			return m_value;
		}
	
		bool next() {
			if (room == 0) return true;
			char* start = ptr;

			while(room && (*ptr != delim)) {
				ptr++;
				room--;
			}
			
			m_value = gxx::buffer(start, ptr - start);
			if (room != 0) {
				ptr++;
				room--;	
			}

			return false;
		}	
	
		iterator begin() {
			next();
			return iterator(*this); 
		}
	
		iterator end() {
			return iterator(*this, true);
		}
	};

	template<typename K, typename T>
	class keys_of_map_t {
		std::map<K,T>& dict;
		typename std::map<K,T>::iterator it;
		typename std::map<K,T>::iterator eit;

		using iterator = gxx::gen<K, keys_of_map_t<K,T>>;
	
	public:
		keys_of_map_t(std::map<K,T>& dict) : dict(dict) {
			it = dict.begin();
			eit = dict.end();
			//dprln(it == eit);
		}
	
		K& value() {
			return const_cast<K&>(it->first);
		}
	
		bool next() {
			it++;
			if (it == eit) return true;
			return false;
		}	
	
		iterator begin() {
			return iterator(*this, dict.empty() ? true : false); 
		}
	
		iterator end() {
			return iterator(*this, true);
		}
	};

    /*template<typename C, typename F>
    class iterate {
        using iterator = gxx::gen<K, keys_of_map_t<K,T>>;
        using rawiterator = typename C::iterator;

        rawiterator it;
        rawiterator eit;

        F&

    public:
        iterate(C& c, F& f) {
            it = c.begin();
            eit = c.end();
        }

        auto& value() {
            return *it;
        }

        bool next() {
            it++;
            if (it == eit) return true;
            return false;
        }

        iterator begin() {
            return iterator(*this, dict.empty() ? true : false);
        }

        iterator end() {
            return iterator(*this, true);
        }
    };

	template<typename K, typename T>
	keys_of_map_t<K,T> keys_of_map(std::map<K,T>& dict) {
		return keys_of_map_t<K,T>(dict);
    }*/
//}

#endif
