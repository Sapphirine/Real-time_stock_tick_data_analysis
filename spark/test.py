# from __future__ import print_function
# import sys

# from pyspark import SparkContext
# from pyspark.streaming import StreamingContext
# from pyspark.streaming.kafka import KafkaUtils

# if __name__ == "__main__":
#     if len(sys.argv) != 3:
#         print("Usage: direct_kafka_wordcount.py <broker_list> <topic>", file=sys.stderr)
#         exit(-1)

#     sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
#     ssc = StreamingContext(sc, 2)

#     brokers, topic = sys.argv[1:]
#     kvs = KafkaUtils.createDirectStream(ssc, [topic], {"metadata.broker.list": brokers})
#     lines = kvs.map(lambda x: x[1])
#     lines.pprint()

#     ssc.start()
#     ssc.awaitTermination()


from __future__ import print_function

import sys
import email
import smtplib
import thread

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils


# def email_thread():
#     to_send = 0
#     s = smtplib.SMTP("smtp.live.com",587)
#     msg = email.message_from_string('warning')
#     msg['From'] = 'rex.yl@hotmail.com'
#     msg['To'] = 'ly2352@columbia.edu'
#     msg['Subject'] = "helOoooOo"
#     s.ehlo() # Hostname to send for this command defaults to the fully qualified domain name of the local host.
#     s.starttls() #Puts connection to SMTP server in TLS mode
#     s.ehlo()
#     s.login('rex.yl@hotmail.com', '111111')
#     while 1:
#         if to_send:
#             print('sent')
#             s.sendmail('rex.yl@hotmail.com', 'ly2352@columbia.edu', 'msg sent')
#             to_send = 0
            

def split_decide(line):
    info = str(line).split(',')
    return info
    # info = 'smaller than 2'
    # if len(info) > 2:
    #     #info[0] = '0'
    #     info = 'bigger than 2'
    #     to_send = 1
    # return info

if __name__ == "__main__":
    #thread.start_new_thread(email_thread,())
    if len(sys.argv) != 3:
        print("Usage: kafka_wordcount.py <zk> <topic>", file=sys.stderr)
        exit(-1)

    sc = SparkContext(appName="PythonStreamingKafkaPriceStream")
    ssc = StreamingContext(sc, 1)

    zkQuorum, topic = sys.argv[1:]
    kvs = KafkaUtils.createStream(ssc, zkQuorum, "spark-streaming-consumer", {topic: 1})
    lines = kvs.map(lambda x: x[1])
    # tmp = lines.map(split_decide)
    # res = tmp.reduce(lambda x,y:x+y)
    lines.pprint()
    #info = str(lines).split(',')
    
    ssc.start()
    ssc.awaitTermination()