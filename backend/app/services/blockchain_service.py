from web3 import Web3
from flask import current_app
import hashlib
import logging
import time
import json
import uuid

class BlockchainService:
    def __init__(self):
        """
        Initialize the blockchain service with Ethereum connection
        """
        self.infura_url = current_app.config.get('INFURA_URL')
        self.contract_address = current_app.config.get('CONTRACT_ADDRESS')
        self.signer_key = current_app.config.get('SIGNER_PRIVATE_KEY')
        
        # Hash storage for simulated blockchain in dev/test environments
        # In production, this would be actual blockchain transactions
        self._simulated_records = {}

        if not all([self.infura_url, self.contract_address, self.signer_key]):
            logging.warning("Blockchain configuration incomplete. Blockchain interactions will be simulated.")
            self.blockchain_enabled = False
        else:
            try:
                self.w3 = Web3(Web3.HTTPProvider(self.infura_url))
                # Check connection
                if not self.w3.is_connected():
                    logging.warning("Could not connect to Ethereum node. Falling back to simulation mode.")
                    self.blockchain_enabled = False
                else:
                    # For a real implementation, you would load the contract ABI here
                    # This is a simplified example
                    logging.info("Connected to Ethereum blockchain successfully.")
                    self.blockchain_enabled = True
            except Exception as e:
                logging.error(f"Error initializing blockchain connection: {e}")
                self.blockchain_enabled = False

    def record_grade(self, grade):
        """
        Records a grade on the blockchain
        Returns the transaction hash
        
        Args:
            grade (str): The grade/feedback to record (can be JSON string or plain text)
            
        Returns:
            str: The transaction hash or simulated hash
        """
        # Generate a unique record ID
        record_id = str(uuid.uuid4())
        timestamp = int(time.time())
        
        if not self.blockchain_enabled:
            # Simulate blockchain recording if not configured
            # Create a deterministic but unique hash based on grade and time
            data = f"{grade}_{timestamp}_{record_id}"
            simulated_hash = "0x" + hashlib.sha256(data.encode()).hexdigest()
            
            # Store the record in our simulation storage
            self._simulated_records[simulated_hash] = {
                'grade': grade,
                'timestamp': timestamp,
                'record_id': record_id
            }
            
            logging.info(f"Simulated blockchain record created: {simulated_hash[:10]}...")
            return simulated_hash
        
        try:
            # This is a placeholder for actual blockchain interaction
            # In a real implementation, you would:
            # 1. Create a transaction to the smart contract
            # 2. Sign it with the private key
            # 3. Send it to the Ethereum network
            # 4. Return the transaction hash
            
            # Example (not functional without contract ABI):
            # nonce = self.w3.eth.get_transaction_count(
            #     self.w3.eth.account.from_key(self.signer_key).address)
            # 
            # tx = self.contract.functions.recordGrade(
            #     record_id, 
            #     Web3.to_hex(text=grade),
            #     timestamp
            # ).build_transaction({
            #     'chainId': 1,  # Ethereum mainnet
            #     'gas': 100000,
            #     'gasPrice': self.w3.eth.gas_price,
            #     'nonce': nonce,
            # })
            # 
            # signed_tx = self.w3.eth.account.sign_transaction(tx, private_key=self.signer_key)
            # tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            # return self.w3.to_hex(tx_hash)
            
            # For now, we'll return a simulated hash
            data = f"{grade}_{timestamp}_{record_id}"
            simulated_hash = "0x" + hashlib.sha256(data.encode()).hexdigest()
            
            # Store in simulation for verification later
            self._simulated_records[simulated_hash] = {
                'grade': grade,
                'timestamp': timestamp,
                'record_id': record_id
            }
            
            logging.info(f"Blockchain-simulation record created: {simulated_hash[:10]}...")
            return simulated_hash
            
        except Exception as e:
            logging.error(f"Error recording grade on blockchain: {e}")
            # Return a fallback hash to avoid breaking the application
            data = f"error_{grade}_{timestamp}_{record_id}"
            fallback_hash = "0x" + hashlib.sha256(data.encode()).hexdigest()
            
            # Store in simulation for verification later
            self._simulated_records[fallback_hash] = {
                'grade': grade,
                'timestamp': timestamp,
                'record_id': record_id,
                'error': str(e)
            }
            
            return fallback_hash
            
    def verify_grade(self, hash_value, expected_grade=None):
        """
        Verifies if a grade exists on the blockchain with the given hash
        
        Args:
            hash_value (str): The transaction hash to verify
            expected_grade (str, optional): If provided, checks if the stored grade matches
            
        Returns:
            dict: Verification result with status and details
        """
        if not hash_value:
            return {
                'verified': False,
                'reason': 'No hash provided',
                'details': None
            }
        
        if not self.blockchain_enabled:
            # Use simulation storage to verify
            if hash_value in self._simulated_records:
                record = self._simulated_records[hash_value]
                
                # If expected grade was provided, check it
                if expected_grade and record.get('grade') != expected_grade:
                    return {
                        'verified': False,
                        'reason': 'Grade mismatch',
                        'details': {
                            'stored_timestamp': record.get('timestamp'),
                            'hash': hash_value
                        }
                    }
                
                return {
                    'verified': True,
                    'reason': 'Verified in simulation storage',
                    'details': {
                        'stored_timestamp': record.get('timestamp'),
                        'hash': hash_value
                    }
                }
            else:
                return {
                    'verified': False,
                    'reason': 'Hash not found in simulation storage',
                    'details': None
                }
        
        try:
            # In a real implementation, you would:
            # 1. Get the transaction receipt from the blockchain
            # 2. Decode the event logs to extract the stored grade
            # 3. Verify it matches the expected grade
            
            # Example (not functional without contract ABI):
            # tx_receipt = self.w3.eth.get_transaction_receipt(hash_value)
            # if not tx_receipt or tx_receipt.status != 1:
            #    return {'verified': False, 'reason': 'Transaction failed or not found'}
            #
            # # Process logs to extract grade data
            # logs = self.contract.events.GradeRecorded().process_receipt(tx_receipt)
            # if not logs:
            #    return {'verified': False, 'reason': 'No grade event found in transaction'}
            #
            # stored_grade = logs[0].args.grade
            # if expected_grade and stored_grade != expected_grade:
            #    return {'verified': False, 'reason': 'Grade mismatch'}
            #
            # return {'verified': True, 'details': {'stored_grade': stored_grade}}
            
            # Fallback to simulation for now
            if hash_value in self._simulated_records:
                record = self._simulated_records[hash_value]
                
                if expected_grade and record.get('grade') != expected_grade:
                    return {
                        'verified': False,
                        'reason': 'Grade mismatch',
                        'details': {
                            'stored_timestamp': record.get('timestamp'),
                            'hash': hash_value[:10] + '...'
                        }
                    }
                
                return {
                    'verified': True,
                    'reason': 'Verified in blockchain simulation',
                    'details': {
                        'stored_timestamp': record.get('timestamp'),
                        'hash': hash_value[:10] + '...'
                    }
                }
            else:
                return {
                    'verified': False,
                    'reason': 'Hash not found in blockchain',
                    'details': None
                }
                
        except Exception as e:
            logging.error(f"Error verifying grade on blockchain: {e}")
            return {
                'verified': False,
                'reason': f'Verification error: {str(e)}',
                'details': None
            }