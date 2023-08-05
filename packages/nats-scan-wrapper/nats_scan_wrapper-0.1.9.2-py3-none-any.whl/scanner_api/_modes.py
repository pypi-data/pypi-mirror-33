"""Задача каждого mode принять decode_data пришедших из NATS,
отработать с помощью ползовательских функций, и вернуть массив с результатами
TODO запускать функцию workera в отдельном процессе
"""

import asyncio
import logging


async def process_mode(context, data, meta, new_pipeline):
    line_buffer = []
    # User input_handler here, you can set this args
    args = context.config["input_handler"](data, meta)

    stderr = {}
    if not context.config["print_stderr"]:
        stderr["stderr"] = asyncio.subprocess.DEVNULL

    create = asyncio.create_subprocess_exec(
        *args,
        stdout=asyncio.subprocess.PIPE,
        **stderr)
    logging.info("Create process %s", args[0])

    proc = await create

    while True:
        try:
            if context.config["readline"]:
                line = await proc.stdout.readline()
                if line.decode().strip() == "":
                    # FIX FOR MASSCAN. REMOVE THAT IN NEW MODE!
                    break
            else:
                line, stderr = await proc.communicate()
                line_buffer.append(line)
                break
        except Exception as e:
            print(e, e.with_traceback, e.args)
            break

        logging.info("Process output: '%s'", line)

        if context.config['chunked_send']:
            result_array = context.config["output_handler"](line)
            packages = context.make_packages(data, meta, result_array)
            # if new_pipeline:
            #     await context.nats_publisher(new_pipeline, packages)
            #     logging.info("Sent to '%s': '%s'",
            #                  new_pipeline, packages)
            logging.info("Result: %s", packages)
            if context.config["send_meta"]:
                await context.nats_report_publisher(
                    data,
                    meta,
                    result_array,
                    scan_status="chunked",
                    new_pipeline=new_pipeline,
                )

                logging.info("Report has been sended.")
            logging.info("Line processed.")
        else:
            line_buffer.append(line)

    await proc.wait()

    if not context.config['chunked_send']:
        result_array = context.config["output_handler"](line_buffer)
        packages = context.make_packages(data, meta, result_array)
        # if new_pipeline:
        #     await context.nats_publisher(new_pipeline, packages)
        #     logging.info("Sent to '%s': '%s'",
        #                  new_pipeline, packages)
        logging.info("Result: %s", packages)
        if context.config["send_meta"]:
            await context.nats_report_publisher(
                data,
                meta,
                result_array,
                scan_status="full",
                new_pipeline=new_pipeline,
            )
            logging.info("Report has been sended.")
        logging.info("Line array processed.")
    logging.info("'%s' completed.", args[0])


async def function_mode_old(context, data, meta, new_pipeline):
    logging.info("Starting '%s' worker function.", context.config["name"])
    # Scanning (start function)
    result_array = context.config["worker_function"](new_pipeline, data, meta)

    if type(result_array) != list:
        result_array = [result_array]
    packages = context.make_packages(data, meta, result_array)

    logging.info("Result: %s", packages)
    if context.config["send_meta"]:
        await context.nats_report_publisher(
            data,
            meta,
            result_array,
            scan_status="full",
            new_pipeline=new_pipeline,
        )
        logging.info("Report has been sended.")
