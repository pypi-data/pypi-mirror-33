import pika
import time
from multiprocessing import Process, Event
import traceback

hostname = 'localhost'
port = 5672
recreate = True


def func_hb(q1, q2, hb_interval):

    try:

        mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
        mq_channel = mq_connection.channel()

        # Heartbeat request signal sent to task manager via rpc-queue
        mq_channel.basic_publish(exchange='', routing_key=q1, body='request')
        print 'Sent heartbeat request'

        if recreate:
            mq_connection.close()

        # Sleep for hb_interval and then check if tmgr responded
        if not recreate:
            mq_connection.sleep(hb_interval)
        else:
            time.sleep(hb_interval)

        if recreate:
            mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
            mq_channel = mq_connection.channel()

        method_frame, props, body = mq_channel.basic_get(queue=q2)

        if body:
            print 'Received heartbeat response: %s' % body
            mq_channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        mq_connection.close()

    except Exception as ex:

        print 'Error: %s' % ex
        print traceback.format_exc()


def func_tmgr(q1, q2, hb_interval):

    try:

        mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
        mq_channel = mq_connection.channel()

        response = False
        while not response:

            method_frame, props, body = mq_channel.basic_get(queue=q1)

            if body:
                print 'Received heartbeat request: %s' % body
                response = True

                mq_channel.basic_ack(delivery_tag=method_frame.delivery_tag)

        if recreate:
            mq_connection.close()

        # Sleep for hb_interval and then check if tmgr responded
        if not recreate:
            mq_connection.sleep(hb_interval/2)
        else:
            time.sleep(hb_interval/2)

        if recreate:
            mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
            mq_channel = mq_connection.channel()

        # Heartbeat request signal sent to task manager via rpc-queue
        mq_channel.basic_publish(exchange='', routing_key=q2, body='response')
        print 'Sent heartbeat response'

        mq_connection.close()

    except Exception as ex:

        print 'Error: %s' % ex
        print traceback.format_exc()


if __name__ == '__main__':

    for hb_interval in [180,180,180]:

        try:
            print '-------------------------------------------------------------'
            print 'Interval: ', hb_interval, ' Recreate: ', recreate

            start = time.time()
            mq_connection = pika.BlockingConnection(pika.ConnectionParameters(host=hostname, port=port))
            mq_channel = mq_connection.channel()

            q1 = 'test-1'
            q2 = 'test-2'

            mq_channel.queue_delete(q1)
            mq_channel.queue_declare(q1)
            mq_channel.queue_delete(q2)
            mq_channel.queue_declare(q2)

            mq_connection.close()

            hb = Process(target=func_hb, args=(q1, q2, hb_interval), name='heartbeat')
            tmgr = Process(target=func_tmgr, args=(q1, q2, hb_interval), name='tmgr')

            hb.start()
            tmgr.start()

            hb.join()
            tmgr.join()
            print 'Time: ', (time.time() - start) - hb_interval

            print '-------------------------------------------------------------'

        except Exception as ex:

            print 'Execution with interval %s failed, error: ex'%hb_interval
