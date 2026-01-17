from flask import Blueprint, request, jsonify
from src.models.user import db
from src.models import Supplier, Ingredient, SupplierIngredient
from src.services.supplier_intelligence import SupplierIntelligenceService
from sqlalchemy import or_, and_, desc
from datetime import datetime

intelligence_bp = Blueprint('intelligence', __name__)
intelligence_service = SupplierIntelligenceService()

@intelligence_bp.route('/intelligence/discover-suppliers', methods=['POST'])
def discover_suppliers():
    """
    Discover potential suppliers for a given ingredient
    """
    try:
        data = request.get_json()
        ingredient_name = data.get('ingredient_name')
        region = data.get('region')
        
        if not ingredient_name:
            return jsonify({'error': 'Ingredient name is required'}), 400
        
        discovered_suppliers = intelligence_service.discover_suppliers(
            ingredient_name=ingredient_name,
            region=region
        )
        
        return jsonify({
            'discovered_suppliers': discovered_suppliers,
            'total_found': len(discovered_suppliers),
            'search_criteria': {
                'ingredient_name': ingredient_name,
                'region': region
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@intelligence_bp.route('/intelligence/evaluate-supplier/<int:supplier_id>', methods=['GET'])
def evaluate_supplier(supplier_id):
    """
    Get comprehensive supplier evaluation
    """
    try:
        evaluation = intelligence_service.evaluate_supplier_performance(supplier_id)
        
        if 'error' in evaluation:
            return jsonify(evaluation), 404
        
        return jsonify(evaluation)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@intelligence_bp.route('/intelligence/optimize-pricing', methods=['POST'])
def optimize_pricing():
    """
    Analyze pricing across suppliers and provide optimization recommendations
    """
    try:
        data = request.get_json()
        ingredient_id = data.get('ingredient_id')
        quantity = data.get('quantity')
        
        if not ingredient_id or not quantity:
            return jsonify({'error': 'Ingredient ID and quantity are required'}), 400
        
        pricing_analysis = intelligence_service.optimize_pricing(
            ingredient_id=ingredient_id,
            quantity=float(quantity)
        )
        
        if 'error' in pricing_analysis:
            return jsonify(pricing_analysis), 404
        
        return jsonify(pricing_analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@intelligence_bp.route('/intelligence/market-intelligence/<category>', methods=['GET'])
def get_market_intelligence(category):
    """
    Get market intelligence for ingredient category
    """
    try:
        market_data = intelligence_service.get_market_intelligence(category)
        return jsonify(market_data)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@intelligence_bp.route('/intelligence/supplier-recommendations', methods=['GET'])
def get_supplier_recommendations():
    """
    Get intelligent supplier recommendations based on various criteria
    """
    try:
        # Get query parameters
        ingredient_category = request.args.get('category')
        min_score = float(request.args.get('min_score', 4.0))
        region = request.args.get('region')
        sustainability_focus = request.args.get('sustainability_focus', 'false').lower() == 'true'
        
        # Build query
        query = Supplier.query.filter(
            Supplier.overall_score >= min_score,
            Supplier.active_status == True
        )
        
        if region:
            query = query.filter(Supplier.country.ilike(f'%{region}%'))
        
        if sustainability_focus:
            query = query.filter(Supplier.sustainability_score >= 4.0)
        
        suppliers = query.order_by(desc(Supplier.overall_score)).limit(10).all()
        
        recommendations = []
        for supplier in suppliers:
            # Get supplier specialties
            specialties = []
            if supplier.specialties:
                try:
                    specialties = json.loads(supplier.specialties) if isinstance(supplier.specialties, str) else supplier.specialties
                except:
                    specialties = []
            
            # Filter by ingredient category if specified
            if ingredient_category and specialties:
                if not any(ingredient_category.lower() in specialty.lower() for specialty in specialties):
                    continue
            
            recommendation = {
                'supplier': supplier.to_dict(),
                'recommendation_score': supplier.overall_score,
                'reasons': [],
                'risk_factors': []
            }
            
            # Add recommendation reasons
            if supplier.overall_score >= 4.5:
                recommendation['reasons'].append('Excellent overall performance rating')
            
            if supplier.verified_status:
                recommendation['reasons'].append('Verified supplier with proven track record')
            
            if supplier.sustainability_score >= 4.5:
                recommendation['reasons'].append('Outstanding sustainability practices')
            
            if supplier.quality_score >= 4.5:
                recommendation['reasons'].append('Superior quality standards')
            
            # Add risk factors
            if supplier.overall_score < 4.0:
                recommendation['risk_factors'].append('Below average performance rating')
            
            if not supplier.verified_status:
                recommendation['risk_factors'].append('Unverified supplier - requires due diligence')
            
            recommendations.append(recommendation)
        
        return jsonify({
            'recommendations': recommendations,
            'total_found': len(recommendations),
            'criteria': {
                'ingredient_category': ingredient_category,
                'min_score': min_score,
                'region': region,
                'sustainability_focus': sustainability_focus
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@intelligence_bp.route('/intelligence/price-trends/<int:ingredient_id>', methods=['GET'])
def get_price_trends(ingredient_id):
    """
    Get price trends and forecasts for an ingredient
    """
    try:
        ingredient = Ingredient.query.get(ingredient_id)
        if not ingredient:
            return jsonify({'error': 'Ingredient not found'}), 404
        
        # Simulate price trend data
        import random
        from datetime import datetime, timedelta
        
        # Generate historical price data (last 12 months)
        historical_data = []
        base_price = ingredient.price_range_min or 100
        current_date = datetime.now() - timedelta(days=365)
        
        for i in range(12):
            price_variation = random.uniform(-0.15, 0.15)  # ±15% variation
            price = base_price * (1 + price_variation)
            
            historical_data.append({
                'month': current_date.strftime('%Y-%m'),
                'average_price': round(price, 2),
                'price_change': round(price_variation * 100, 1)
            })
            
            current_date += timedelta(days=30)
            base_price = price  # Use previous price as base for next month
        
        # Generate forecast (next 6 months)
        forecast_data = []
        for i in range(6):
            price_variation = random.uniform(-0.10, 0.10)  # ±10% variation for forecast
            price = base_price * (1 + price_variation)
            
            forecast_data.append({
                'month': current_date.strftime('%Y-%m'),
                'predicted_price': round(price, 2),
                'confidence_level': random.choice(['high', 'medium', 'low']),
                'price_change': round(price_variation * 100, 1)
            })
            
            current_date += timedelta(days=30)
            base_price = price
        
        trend_analysis = {
            'ingredient_id': ingredient_id,
            'ingredient_name': ingredient.name,
            'current_price_range': {
                'min': ingredient.price_range_min,
                'max': ingredient.price_range_max
            },
            'historical_data': historical_data,
            'forecast_data': forecast_data,
            'trend_summary': {
                'overall_trend': random.choice(['increasing', 'stable', 'decreasing']),
                'volatility': random.choice(['high', 'medium', 'low']),
                'seasonal_pattern': random.choice(['strong', 'moderate', 'weak']),
                'market_factors': [
                    'Supply chain disruptions',
                    'Regulatory changes',
                    'Demand fluctuations',
                    'Raw material costs'
                ]
            },
            'recommendations': [
                'Monitor price movements closely',
                'Consider forward contracts for price stability',
                'Evaluate alternative suppliers',
                'Assess inventory optimization opportunities'
            ]
        }
        
        return jsonify(trend_analysis)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@intelligence_bp.route('/intelligence/competitive-analysis', methods=['POST'])
def competitive_analysis():
    """
    Perform competitive analysis across suppliers for specific requirements
    """
    try:
        data = request.get_json()
        ingredient_ids = data.get('ingredient_ids', [])
        requirements = data.get('requirements', {})
        
        if not ingredient_ids:
            return jsonify({'error': 'At least one ingredient ID is required'}), 400
        
        analysis_results = []
        
        for ingredient_id in ingredient_ids:
            ingredient = Ingredient.query.get(ingredient_id)
            if not ingredient:
                continue
            
            # Get supplier offerings for this ingredient
            offerings = SupplierIngredient.query.filter_by(
                ingredient_id=ingredient_id
            ).all()
            
            supplier_analysis = []
            for offering in offerings:
                supplier = Supplier.query.get(offering.supplier_id)
                if not supplier:
                    continue
                
                # Calculate competitive score
                competitive_score = intelligence_service._calculate_value_score(
                    offering, supplier, requirements.get('quantity', 100)
                )
                
                supplier_analysis.append({
                    'supplier_name': supplier.company_name,
                    'supplier_id': supplier.id,
                    'price_per_kg': offering.price_per_kg,
                    'lead_time_days': offering.lead_time_days,
                    'minimum_order_quantity': offering.minimum_order_quantity,
                    'quality_score': supplier.quality_score,
                    'reliability_score': supplier.reliability_score,
                    'sustainability_score': supplier.sustainability_score,
                    'overall_score': supplier.overall_score,
                    'competitive_score': competitive_score,
                    'strengths': [],
                    'weaknesses': []
                })
            
            # Sort by competitive score
            supplier_analysis.sort(key=lambda x: x['competitive_score'], reverse=True)
            
            # Add strengths and weaknesses
            for i, analysis in enumerate(supplier_analysis):
                if i == 0:
                    analysis['strengths'].append('Best overall value proposition')
                
                if analysis['price_per_kg'] == min(s['price_per_kg'] for s in supplier_analysis if s['price_per_kg']):
                    analysis['strengths'].append('Lowest price')
                
                if analysis['quality_score'] >= 4.5:
                    analysis['strengths'].append('Superior quality')
                
                if analysis['sustainability_score'] >= 4.5:
                    analysis['strengths'].append('Excellent sustainability')
                
                if analysis['lead_time_days'] and analysis['lead_time_days'] <= 14:
                    analysis['strengths'].append('Fast delivery')
                
                # Weaknesses
                if analysis['overall_score'] < 4.0:
                    analysis['weaknesses'].append('Below average performance')
                
                if analysis['price_per_kg'] == max(s['price_per_kg'] for s in supplier_analysis if s['price_per_kg']):
                    analysis['weaknesses'].append('Highest price')
                
                if analysis['lead_time_days'] and analysis['lead_time_days'] > 30:
                    analysis['weaknesses'].append('Long delivery time')
            
            analysis_results.append({
                'ingredient_id': ingredient_id,
                'ingredient_name': ingredient.name,
                'supplier_analysis': supplier_analysis,
                'market_summary': {
                    'total_suppliers': len(supplier_analysis),
                    'price_range': {
                        'min': min(s['price_per_kg'] for s in supplier_analysis if s['price_per_kg']),
                        'max': max(s['price_per_kg'] for s in supplier_analysis if s['price_per_kg'])
                    } if supplier_analysis else None,
                    'average_lead_time': sum(s['lead_time_days'] for s in supplier_analysis if s['lead_time_days']) / len([s for s in supplier_analysis if s['lead_time_days']]) if supplier_analysis else None
                }
            })
        
        return jsonify({
            'competitive_analysis': analysis_results,
            'analysis_date': datetime.utcnow().isoformat(),
            'requirements': requirements
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

