#ifndef GXX_SPAM_SERVER_H
#define GXX_SPAM_SERVER_H

#include <gxx/inet/tcp_server.h>
#include <algorithm>
#include <list>

#include <string.h>
#include <gxx/debug.h>

namespace gxx {
	namespace inet {
		class tcpspam_server : public inet::tcp_server, public io::ostream {
			std::list<gxx::inet::tcp_socket> clients;
	
		public:
			tcpspam_server() = default;
			tcpspam_server(int port) {
				start(port);
			}
	
			int start(int port) {
				inet::tcp_server::init();
				inet::tcp_server::bind(port);
				inet::tcp_server::listen(10);
				inet::tcp_server::nonblock(true);
				return 0;
			}	
			int __send(const char* str) {
				return __send(str, strlen(str));
			};
	
			int __send(const char* str, size_t n) {
				while(true) {
					gxx::inet::tcp_socket newsock = accept();
					if (!newsock.good()) break;
					clients.push_back(newsock);
				}
	
				int ret = 0;
				auto it = clients.begin();
				decltype(it) cit;
				auto eit = clients.end();
				while(it != eit) {
					cit = it; ++it;
					ret = cit->write(str, n);
					if (ret < 0) {
						clients.erase(cit);
					}
				}
				
				/*if (needRemove)	{ 
					std::list<gxx::socket>::iterator it;
					auto next = clients.begin();
					auto end = clients.end();
					it = next;
					for(; it != end; it = next) {
						next++;
						if (it->is_connected() == false) clients.erase(it);
					}
				}*/
	
	
				return ret;
			}
	
			int writeData(const char* str, size_t sz) override {
				return __send(str, sz);
			}	
	
			void drop_all() {
				for (auto& c : clients) {
					c.close();
				}
				clients.clear();
			}
		};
	}
}

#endif
