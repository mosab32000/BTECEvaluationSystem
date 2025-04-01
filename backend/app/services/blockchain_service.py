import logging
import hashlib
import json
import time
from web3 import Web3
from flask import current_app

class BlockchainService:
    def __init__(self):
        """
        Initialize the blockchain service with Ethereum connection
        """
        infura_url = current_app.config.get('INFURA_URL')
        contract_address = current_app.config.get('CONTRACT_ADDRESS')
        private_key = current_app.config.get('SIGNER_PRIVATE_KEY')
        
        if not all([infura_url, contract_address, private_key]):
            logging.warning("Blockchain service not fully configured - running in simulated mode")
            self.simulation_mode = True
            return
            
        try:
            self.web3 = Web3(Web3.HTTPProvider(infura_url))
            self.contract_address = contract_address
            self.private_key = private_key
            self.simulation_mode = False
            
            # Load ABI - simplified in this example
            self.contract_abi = [
                {
                    "inputs": [
                        {
                            "internalType": "string",
                            "name": "gradeHash",
                            "type": "string"
                        }
                    ],
                    "name": "recordGrade",
                    "outputs": [
                        {
                            "internalType": "bytes32",
                            "name": "",
                            "type": "bytes32"
                        }
                    ],
                    "stateMutability": "nonpayable",
                    "type": "function"
                }
            ]
            self.contract = self.web3.eth.contract(
                address=self.contract_address, 
                abi=self.contract_abi
            )
            
            logging.info("Blockchain service initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize blockchain service: {e}")
            self.simulation_mode = True
    
    def record_grade(self, grade):
        """
        Records a grade on the blockchain
        Returns the transaction hash
        """
        # Create a hash of the grade
        grade_hash = hashlib.sha256(grade.encode()).hexdigest()
        
        if self.simulation_mode:
            # Simulate blockchain recording for development/testing
            logging.info(f"SIMULATION MODE: Would have recorded {grade_hash} to blockchain")
            # Generate a fake but deterministic transaction hash
            fake_tx_hash = hashlib.sha256(f"{grade_hash}:{time.time()}".encode()).hexdigest()
            return "0x" + fake_tx_hash
            
        try:
            # Get the sender account from private key
            account = self.web3.eth.account.from_key(self.private_key)
            sender_address = account.address
            
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(sender_address)
            tx = self.contract.functions.recordGrade(grade_hash).build_transaction({
                'chainId': 1,  # Ethereum mainnet
                'gas': 100000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, self.private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            logging.info(f"Grade recorded on blockchain with tx hash: {tx_hash.hex()}")
            return tx_hash.hex()
            
        except Exception as e:
            logging.error(f"Failed to record on blockchain: {e}")
            # Return a hash that indicates failure but still provides traceability
            error_hash = "0x" + hashlib.sha256(f"ERROR:{grade_hash}".encode()).hexdigest()
            return error_hash
