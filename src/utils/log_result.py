import logging

def logResult(output_path, result):
    logging.basicConfig(
        filename = output_path,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='[%Y-%m-%d %H:%M:%S]'
    )
    
    logging.info(result)
    
    