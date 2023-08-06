#ifndef GXX_SERIALIZE_SCPI_H
#define GXX_SERIALIZE_SCPI_H

#include <vector>
#include <string>
#include <cctype>

#include <gxx/creader.h>
#include <gxx/print/stdprint.h>

namespace gxx {
	using buffer_literal::operator"" _b;

	class scpi_string_parser {
	public:
		struct header {
			std::string str;
			int num;
			header(const std::string& str, int num) : str(str), num(num) {}
			size_t printTo(gxx::io::ostream& o) const {
				if (num == -1) return gxx::print(str);
				else return gxx::fprint_to(o, "{}{}", str, num);
			}
		};

		std::vector<header> 		headers;
		std::vector<std::string> 	arguments;
		bool is_question = false;
		bool is_error = false;

	public:
		scpi_string_parser(const std::string& str) {
			gxx::creader reader(str.c_str());

			while(reader.next_is(isalpha)) {
				std::string tempstr = reader.string_while(isalpha);
				int tempnum = reader.next_is(isdigit) ? reader.integer() : -1;
				headers.emplace_back(tempstr, tempnum);
				if (!reader.next_is(':')) break;
				else reader.skip(); 
			}
	
			reader.skip_while(" ,\n");
			while(!reader.next_is("\0?"_b)) {
				if (reader.next_is('\"')) {
                                        reader.skip();
                                        arguments.emplace_back(reader.string_while(gxx::chars_set_checker("\"\0", false)));
					if (reader.next_is('\0')) return;
					else reader.skip();
				} else {
                                        arguments.emplace_back(reader.string_while(gxx::chars_set_checker(" ,\0\n?", false)));
				}
				reader.skip_while(" ,\n");
			}
	
			if (reader.next_is('?')) is_question = true;

                        //gxx::println(arguments);
		}

		size_t printTo(gxx::io::ostream& o) const {
			return gxx::fprint_to(o, "({}, {})", headers, arguments);
		}
	};
}

#endif
