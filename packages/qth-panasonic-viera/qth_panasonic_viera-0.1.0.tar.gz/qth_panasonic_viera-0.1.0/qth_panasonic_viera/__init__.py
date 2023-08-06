import sys
import asyncio
from argparse import ArgumentParser

import qth
import panasonic_viera

from .version import __version__


loop = asyncio.get_event_loop()

async def async_main(client, tv, qth_path_prefix, update_interval):
    power_path = "{}power".format(qth_path_prefix)
    
    await client.register(power_path, qth.PROPERTY_MANY_TO_ONE,
                    description="TV power state",
                    delete_on_unregister=True)
    
    async def is_tv_on():
        """Determine if the TV is currently powered on."""
        # A hack: TV doesn't respond to volume command if its off.
        try:
            volume = await loop.run_in_executor(None, tv.get_volume)
            return True
        except:
            return False
    
    power_property = None
    async def on_power_change(topic, desired_state):
        nonlocal power_property
        power_property = desired_state
        
        actual_state = await is_tv_on()
        
        if bool(desired_state) != actual_state:
            # NB: Actually sends 'power button' command which toggles power
            # state!
            tv.turn_off()
    await client.watch_event(power_path, on_power_change)
    
    # Update the property when the TV state changes by itself (e.g. due to
    # remote).
    async def update_power_state():
        nonlocal power_property
        
        tv_state = await is_tv_on()
        if power_property is None or bool(power_property) != tv_state:
            power_property = tv_state
            await client.set_property(power_path, power_property)
        
        loop.call_later(update_interval, loop.create_task, update_power_state())
    await update_power_state()

def main():
    parser = ArgumentParser(
        description="Control a Panasonic VIERA TV")
    parser.add_argument("tv_hostname", help="IP or Hostname of TV to control")
    parser.add_argument("qth_path_prefix", help="Qth path prefix.")
    parser.add_argument("--update-interval", "-i", default=1.0, type=float,
                        help="Update interval for power state in seconds. "
                             "(default %(default)s).")
    
    parser.add_argument("--host", "-H", default=None,
                        help="Qth server hostname.")
    parser.add_argument("--port", "-P", default=None, type=int,
                        help="Qth server port.")
    parser.add_argument("--keepalive", "-K", default=10, type=int,
                        help="MQTT Keepalive interval (seconds).")
    parser.add_argument("--version", "-V", action="version",
                        version="%(prog)s {}".format(__version__))
    args = parser.parse_args()
    
    client = qth.Client(
        "qth_panasonic_viera", "Panasonic VIERA TV control.",
        loop=loop,
        host=args.host,
        port=args.port,
        keepalive=args.keepalive,
    )
    tv = panasonic_viera.RemoteControl(args.tv_hostname)
    
    loop.run_until_complete(async_main(client, tv,
                                       args.qth_path_prefix,
                                       args.update_interval))
    loop.run_forever()

if __name__ == "__main__":
    main()
