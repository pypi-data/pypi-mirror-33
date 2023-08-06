#ifndef GENOS_FDRING_STORAGE_H
#define GENOS_FDRING_STORAGE_H

#include <mutex>
#include <gxx/event/once_delegate.h>
#include <gxx/io/iostorage.h>
#include <gxx/bytering.h>
#include <unistd.h>
#include <thread>

#include <gxx/event/flag.h>

namespace gxx {
	namespace io {
		
		class fdring_istorage : public gxx::io::istorage {
			int fd;
			gxx::bytering rxring;
			//gxx::once_delegate_flag flag;
			
			gxx::event::flag* flg = nullptr;

			std::mutex rxmtx;
			std::thread thr;
		public:

			fdring_istorage(int fd, gxx::buffer buf) : rxring(buf), fd(fd) {}
		
			void readfunc() {
				while(true) {
					char c;
					int sts = ::read(fd, &c, 1);
					
					if (sts <= 0) {
						dprln("fdring_istorage: bad");
						exit(0);
					} else {
						rxmtx.lock();
						rxring.push(c);
						rxmtx.unlock();
						if (flg) flg->set();								
					}
				}
			}

			int start() {
				thr = std::thread(&fdring_istorage::readfunc, this);
			}

		protected:
			int readData(char* data, size_t size) override {
				std::lock_guard<std::mutex> lock(rxmtx); 
				int ret = rxring.popn(data, size);
				if (flg && rxring.empty()) flg->clr();
				return ret;
			}		
		public:
			int avail() override {
				std::lock_guard<std::mutex> lock(rxmtx); 
				return rxring.avail();
			}	

			void set_avail_flag(gxx::event::flag* flg) {
				this->flg = flg;
			}
		};
	}

	/*	class fdring : public gxx::io::ostream, public gxx::io::istorage {
			int fd;
			gxx::bytering rxring;
			gxx::once_delegate_flag flag;

			std::mutex rxmtx;
		public:

			fdring(int fd, gxx::buffer buf) : rxring(buf), fd(fd) {}

		
		protected:

			int writeData(const char* data, size_t size) override {
				::write(fd, data, size);
			}

			int readData(char* data, size_t size) override {
				std::lock_guard<std::mutex> lock(rxmtx); 
				int ret = rxring.popn(data, size);
				if (rxring.empty()) flag.clr();
			}		

			int avail() override {
				std::lock_guard<std::mutex> lock(rxmtx); 
				return rxring.avail();
			}	
		};
	}*/
}

#endif