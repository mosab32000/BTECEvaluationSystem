"""
وحدة التحقق من التقييمات باستخدام تقنية البلوكتشين
"""

import os
import json
import hashlib
from web3 import Web3
from flask import current_app

class BlockchainVerifier:
    """
    فئة للتحقق من صحة التقييمات باستخدام تقنية البلوكتشين
    """
    def __init__(self):
        # تهيئة اتصال Web3
        infura_url = os.environ.get('INFURA_URL') or current_app.config.get('INFURA_URL')
        contract_address = os.environ.get('CONTRACT_ADDRESS') or current_app.config.get('CONTRACT_ADDRESS')
        private_key = os.environ.get('SIGNER_PRIVATE_KEY') or current_app.config.get('SIGNER_PRIVATE_KEY')
        
        # في حالة عدم توفر المعلومات اللازمة، نستخدم وضع المحاكاة
        self.simulation_mode = not all([infura_url, contract_address, private_key])
        
        if self.simulation_mode:
            current_app.logger.warning("تشغيل وحدة التحقق بوضع المحاكاة (بدون اتصال فعلي بالبلوكتشين)")
        else:
            try:
                # إنشاء اتصال Web3
                self.web3 = Web3(Web3.HTTPProvider(infura_url))
                
                # تهيئة العقد الذكي
                # هذا مجرد مثال - في التطبيق الفعلي، يجب تحميل ABI من ملف
                self.contract_abi = [
                    {
                        "inputs": [
                            {"name": "hash", "type": "string"}
                        ],
                        "name": "storeHash",
                        "outputs": [{"name": "success", "type": "bool"}],
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "inputs": [
                            {"name": "hash", "type": "string"}
                        ],
                        "name": "verifyHash",
                        "outputs": [{"name": "exists", "type": "bool"}],
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
                
                self.contract = self.web3.eth.contract(address=contract_address, abi=self.contract_abi)
                self.private_key = private_key
                self.account = self.web3.eth.account.from_key(private_key)
            except Exception as e:
                current_app.logger.error(f"خطأ في تهيئة وحدة التحقق بالبلوكتشين: {str(e)}")
                self.simulation_mode = True
    
    def verify_evaluation(self, evaluation):
        """
        التحقق من صحة تقييم وتسجيله على البلوكتشين
        
        Args:
            evaluation: كائن التقييم المراد التحقق منه
            
        Returns:
            dict: نتيجة التحقق
        """
        # إنشاء بصمة فريدة للتقييم
        evaluation_data = {
            "id": evaluation.id,
            "task_encrypted": evaluation.task_encrypted,
            "grade": evaluation.grade,
            "feedback": evaluation.feedback,
            "grade_numerical": evaluation.grade_numerical,
            "rubric_results": evaluation.rubric_results,
            "submitted_at": evaluation.submitted_at.isoformat() if evaluation.submitted_at else None,
            "evaluated_at": evaluation.evaluated_at.isoformat() if evaluation.evaluated_at else None,
            "user_id": evaluation.user_id
        }
        
        json_data = json.dumps(evaluation_data, sort_keys=True)
        hash_hex = hashlib.sha256(json_data.encode('utf-8')).hexdigest()
        
        if self.simulation_mode:
            # وضع المحاكاة - عدم الاتصال الفعلي بالبلوكتشين
            current_app.logger.info(f"وضع المحاكاة: تم إنشاء البصمة {hash_hex}")
            return {
                "hash": hash_hex,
                "transaction": "0x" + "0" * 64,  # رمز معاملة وهمي
                "verified": True,
                "simulation": True
            }
        else:
            try:
                # إرسال البصمة إلى العقد الذكي
                tx = self.contract.functions.storeHash(hash_hex).build_transaction({
                    'chainId': 1,  # Ethereum Mainnet
                    'gas': 200000,
                    'gasPrice': self.web3.eth.gas_price,
                    'nonce': self.web3.eth.get_transaction_count(self.account.address)
                })
                
                # توقيع وإرسال المعاملة
                signed_tx = self.web3.eth.account.sign_transaction(tx, private_key=self.private_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
                tx_receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
                
                # التحقق من نجاح المعاملة
                if tx_receipt.status == 1:
                    current_app.logger.info(f"تم تسجيل البصمة {hash_hex} بنجاح على البلوكتشين")
                    return {
                        "hash": hash_hex,
                        "transaction": tx_hash.hex(),
                        "verified": True,
                        "block": tx_receipt.blockNumber
                    }
                else:
                    current_app.logger.error(f"فشل في تسجيل البصمة {hash_hex} على البلوكتشين")
                    return {
                        "hash": hash_hex,
                        "transaction": tx_hash.hex(),
                        "verified": False,
                        "error": "فشل المعاملة"
                    }
            
            except Exception as e:
                current_app.logger.error(f"خطأ في التحقق بالبلوكتشين: {str(e)}")
                return {
                    "hash": hash_hex,
                    "verified": False,
                    "error": str(e)
                }
