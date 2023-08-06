#include <gxx/trent/gbson.h>

namespace gxx {
    namespace gbson {
		
        void print_bytes(const gxx::buffer buf, gxx::io::ostream& os) {
			os.putchar(gbson_bytes_type);
            os.write((const char*)&buf.size(), 2);
			os.write(buf.data(), buf.size());		
		}

        void print_list(const gxx::trent::list_type& arr, gxx::io::ostream& os) {
            size_t sz = arr.size();
            os.putchar(gbson_list_type);
            os.write((const char*)&sz, 1);
            for (auto& v : arr) {
                dump(v, os);
            }
        }

        void print_dict(const gxx::trent::dict_type& dict, gxx::io::ostream& os) {
            size_t sz = dict.size();
            os.putchar(gbson_dict_type);
            os.write((const char*)&sz, 1);
            for (auto& d : dict) {
                print_bytes(gxx::buffer(d.first.data(), d.first.size()), os);
                dump(d.second, os);
            }
        }

        void print_numer(gxx::trent::numer_type num, gxx::io::ostream& os) {
            os.putchar(gbson_numer_type);
//            static_assert(sizeof(num) == 8);
            /*uint8_t sz;
            if
                (i64 & 0xFFFFFFFF00000000ll) sz = 8;
            else if
                (i64 & 0xFFFF0000) sz = 4;
            else if
                (i64 & 0xFF00) sz = 2;
            else
                sz = 1;
            os.putchar(sz);*/
            os.write((const char*) &num, sizeof(num));
        }

        void dump(const trent& tr, gxx::io::ostream& os) {
            switch(tr.get_type()) {
                case(gxx::trent::type::numer) :
                    os.putchar(gbson_numer_type);
                    //os.putchar(sizeof(trent::sfloat_type));
                    os.write((const char*)&tr.unsafe_numer_const(), sizeof(trent::numer_type));
					break;


                case(gxx::trent::type::string) :
                    print_bytes(tr.as_buffer(), os);
					break;

                case(gxx::trent::type::list) :
                    print_list(tr.unsafe_list_const(), os);
                    break;

                case(gxx::trent::type::dict) :
                    print_dict(tr.unsafe_dict_const(), os);
					break;
								
			}
		}

        result<trent> parse_numer(gxx::io::istream& is) {
            dprln("integer_type");
            uint8_t sz = 8;
            int64_t res = 0;
            is.read((char*)&res, sz);
            return res;
        }

        result<trent> parse_list(gxx::io::istream& is) {
            dprln("list_type");
            uint8_t sz = is.getchar();
            gxx::trent res(gxx::trent::type::list);
            for(int i = 0; i < sz; ++i) {
                res.unsafe_list().emplace_back(parse(is));
            }
            return res;
        }

        result<trent> parse(gxx::io::istream& is) {
            uint8_t type = is.getchar();

            switch (type) {
                case gbson_numer_type:
                    return parse_numer(is);

                case gbson_list_type:
                    return parse_list(is);

                case gbson_dict_type:
                    dprln("dict_type");
                    break;
            }

            return error("gbson error");
        }
	}
}
