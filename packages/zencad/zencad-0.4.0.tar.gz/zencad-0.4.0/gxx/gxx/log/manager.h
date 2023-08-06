#ifndef GXX_LOG_MANAGER_H
#define GXX_LOG_MANAGER_H

#include <gxx/log/base.h>
#include <memory>

namespace gxx {
	namespace log {
		class target;
		class logmessage;
 
		//void sync_logging(std::shared_ptr<logmessage> logmsg);
		//void async_logging(std::shared_ptr<logmessage> logmsg);
		
		/*void async_manager_send_one();
		void async_manager_send_all();
		void async_manager_avail();
		void async_manager_wait();
		void async_manager_loop();*/
	}
}

#endif