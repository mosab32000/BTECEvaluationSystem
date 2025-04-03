"""
حزمة خدمات نظام تقييم BTEC
توفر خدمات الذكاء الاصطناعي والبلوكتشين وغيرها
"""

from .ai_service import AIEvaluator
from .ai_service_direct import AIEvaluatorDirect
from .ai_service_arabic import AIEvaluatorArabic
from .ai_service_multimodal import AIEvaluatorMultimodal
from .ai_service_advanced import AIEvaluatorAdvanced
from .ai_service_rest import AIEvaluatorREST
from .blockchain_service import BlockchainService

__all__ = [
    'AIEvaluator',
    'AIEvaluatorDirect',
    'AIEvaluatorArabic',
    'AIEvaluatorMultimodal',
    'AIEvaluatorAdvanced',
    'AIEvaluatorREST',
    'BlockchainService'
]