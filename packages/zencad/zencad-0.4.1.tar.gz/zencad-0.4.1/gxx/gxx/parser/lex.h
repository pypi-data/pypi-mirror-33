#ifndef GXX_LEX_H
#define GXX_LEX_H

#include <vector>
#include <gxx/parser/token.h>

namespace gxx { namespace parser {
	std::vector<token> json_tokens(const std::string & text);
}}

#endif