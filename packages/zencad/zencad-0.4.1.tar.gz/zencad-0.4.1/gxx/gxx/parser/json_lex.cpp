#include <gxx/parser/lex.h>
#include <algorithm>

namespace gxx { namespace parser {
    std::vector<token> json_tokens(const std::string & text) {
        std::vector<token> tokens;
        auto it = begin(text);
        while (true)
        {
            it = std::find_if_not(it, end(text), isspace); // Skip whitespace
            if (it == end(text))
            {
                tokens.emplace_back('$');
                return tokens;
            }
            switch (*it)
            {
            case '[': case ']': case ',':
            case '{': case '}': case ':':
                tokens.push_back({ *it++ });
                break;
            case '"':
                {
                    auto it2 = ++it;
                    for (; it2 < end(text); ++it2)
                    {
                        if (*it2 == '"') break;
                        if (*it2 == '\\') ++it2;
                    }
                    if (it2 < end(text))
                    {
                        tokens.emplace_back('"', decode_string(it, it2));
                        it = it2 + 1;
                    }
                    else throw parse_error("String missing closing quote");
                }
                break;
            case '-': case '0': case '1': case '2':
            case '3': case '4': case '5': case '6':
            case '7': case '8': case '9':
                {
                    auto it2 = std::find_if_not(it, end(text), [](char ch) { return isalnum(ch) || ch == '+' || ch == '-' || ch == '.'; });
                    auto num = std::string(it, it2);
                    if (!is_json_number(num)) throw parse_error("Invalid number: " + num);
                    tokens.emplace_back('#', move(num));
                    it = it2;
                }
                break;
            default:
                if (isalpha(*it))
                {
                    auto it2 = std::find_if_not(it, end(text), isalpha);
                    if (std::equal(it, it2, "true")) tokens.emplace_back('t');
                    else if (std::equal(it, it2, "false")) tokens.emplace_back('f');
                    else if (std::equal(it, it2, "null")) tokens.emplace_back('n');
                    else throw parse_error("Invalid token: " + std::string(it, it2));
                    it = it2;
                }
                else throw parse_error("Invalid character: \'" + std::string(1, *it) + '"');
            }
        }
    }
}}