import sys
import os.path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from metal_cloud_sdk.clients.bsi import BSI
from jsonrpc2_base.plugins.client.signature_add import SignatureAdd
from jsonrpc2_base.plugins.client.debug_logger import DebugLogger

class BSIClient(object):
    """
    """
    @staticmethod
    def init():
        # The API key can be found in the interface by accessing myBigstep > Metal Cloud > API credentials
        strAPIKey = "00:pl34s3c0pyth34p1k3yfr0mth3bs14dm1n1nt3rf4c3"
        dictParams = {
            "strJSONRPCRouterURL": "https://fullmetal.bigstep.com/api"
        }

        """
        Instantiate the Python Client.
        """
        bsi = BSI.getInstance(
            dictParams,
            [
                SignatureAdd(strAPIKey, {}),
                DebugLogger(True, "DebugLogger.log")
            ]
        )

        return bsi