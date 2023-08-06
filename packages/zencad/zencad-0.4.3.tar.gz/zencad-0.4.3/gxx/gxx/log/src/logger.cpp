#include <gxx/log/logger2.h>
#include <gxx/log/target2.h>
#include <gxx/print.h>

namespace gxx {
	namespace log {
		void logger::link(target& tgt, level lvl) { targets.push_back(std::make_pair(&tgt,lvl)); }

		void logger::clear_targets() { targets.clear(); }

        void sync_logging(std::shared_ptr<logmessage> logmsg) {
            auto plogger = logmsg->logger;

            for (auto pr : plogger->targets) {
                if (pr.second <= logmsg->level) pr.first->log(logmsg);
            }
        }

		void logger::log(level lvl, std::string&& msg) {
			auto logmsg = std::allocate_shared<logmessage>(gxx::log::alloc);
			//logmsg->time = gxx::time::now();
			logmsg->message = std::move(msg);
			logmsg->level = lvl;
			logmsg->logger = this;

			//if (syncmode) gxx::log::sync_logging(logmsg);
			//else gxx::log::async_logging(logmsg);
			gxx::log::sync_logging(logmsg);
		}
	}
}
