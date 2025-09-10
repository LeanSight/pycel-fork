#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
Practical examples of Model Focusing capabilities in Pycel.

This file contains real examples of how to use the core model focusing
functionalities for industrial analysis of Excel spreadsheets.
"""

import os
import tempfile
from pathlib import Path

from pycel import ExcelCompiler


def example_1_financial_model_audit():
    """
    Example 1: Financial Model Audit
    
    Demonstrates how to extract and validate a critical sub-model
    from a complex financial model.
    """
    print("=== Example 1: Financial Model Audit ===")
    
    # Simulate loading financial model
    # In practice, this would be: ExcelCompiler('financial_model.xlsx')
    excel = create_sample_financial_model()
    
    print(f"Original model: {len(excel.cell_map)} cells")
    
    # Define critical inputs and outputs
    input_addrs = [
        'Assumptions!B1',  # Revenue_Growth
        'Assumptions!B2',  # COGS_Rate
        'Assumptions!B3'   # OpEx_Rate
    ]
    
    output_addrs = [
        'Summary!B1',  # Revenue
        'Summary!B5',  # EBITDA
        'Summary!B6'   # FCF
    ]
    
    print(f"Critical inputs: {input_addrs}")
    print(f"Critical outputs: {output_addrs}")
    
    # Extract sub-model
    excel.trim_graph(input_addrs=input_addrs, output_addrs=output_addrs)
    
    print(f"Trimmed model: {len(excel.cell_map)} cells")
    print(f"Reduction: {((len(excel.cell_map) / len(excel.cell_map)) * 100):.1f}%")
    
    # Validate sub-model accuracy
    validation_results = excel.validate_calcs(output_addrs=output_addrs)
    
    if validation_results:
        print("⚠️ Discrepancies found:")
        for category, errors in validation_results.items():
            print(f"  {category}: {len(errors)} errors")
    else:
        print("✅ Sub-model validated correctly")
    
    # Show current values
    print("\nCurrent values:")
    for addr in output_addrs:
        try:
            value = excel.evaluate(addr)
            print(f"  {addr}: {value:,.2f}" if isinstance(value, (int, float)) else f"  {addr}: {value}")
        except:
            print(f"  {addr}: Not available")
    
    return excel


def example_2_sensitivity_analysis():
    """
    Example 2: Sensitivity Analysis
    
    Demonstrates how to perform sensitivity analysis
    by modifying inputs and observing impact on outputs.
    """
    print("\n=== Example 2: Sensitivity Analysis ===")
    
    # Use model from previous example
    excel = create_sample_financial_model()
    
    # Extract sub-model for analysis
    input_addrs = ['Assumptions!B1', 'Assumptions!B2']  # Revenue_Growth, COGS_Rate
    output_addrs = ['Summary!B5']  # EBITDA
    
    excel.trim_graph(input_addrs=input_addrs, output_addrs=output_addrs)
    
    # Define sensitivity scenarios
    scenarios = [
        {'name': 'Base Case', 'Revenue_Growth': 0.05, 'COGS_Rate': 0.60},
        {'name': 'Optimistic', 'Revenue_Growth': 0.10, 'COGS_Rate': 0.55},
        {'name': 'Pessimistic', 'Revenue_Growth': 0.02, 'COGS_Rate': 0.65},
        {'name': 'High Growth', 'Revenue_Growth': 0.15, 'COGS_Rate': 0.60},
        {'name': 'Cost Pressure', 'Revenue_Growth': 0.05, 'COGS_Rate': 0.70},
    ]
    
    print("Scenario Analysis:")
    print("Scenario".ljust(15) + "Rev Growth".ljust(12) + "COGS Rate".ljust(12) + "EBITDA")
    print("-" * 55)
    
    results = []
    for scenario in scenarios:
        # Configure scenario inputs
        excel.set_value('Assumptions!B1', scenario['Revenue_Growth'])
        excel.set_value('Assumptions!B2', scenario['COGS_Rate'])
        
        # Evaluate output
        try:
            ebitda = excel.evaluate('Summary!B5')
            results.append({
                'scenario': scenario['name'],
                'ebitda': ebitda,
                'revenue_growth': scenario['Revenue_Growth'],
                'cogs_rate': scenario['COGS_Rate']
            })
            
            print(f"{scenario['name']:<15}{scenario['Revenue_Growth']:<12.1%}{scenario['COGS_Rate']:<12.1%}{ebitda:>10,.0f}")
        except Exception as e:
            print(f"{scenario['name']:<15}Error: {str(e)}")
    
    # Individual sensitivity analysis
    print("\nIndividual Sensitivity Analysis (Revenue Growth):")
    excel.set_value('Assumptions!B2', 0.60)  # Fix COGS
    
    growth_rates = [0.00, 0.02, 0.05, 0.08, 0.10, 0.12, 0.15]
    print("Growth Rate".ljust(15) + "EBITDA".ljust(15) + "Change")
    print("-" * 40)
    
    base_ebitda = None
    for rate in growth_rates:
        excel.set_value('Assumptions!B1', rate)
        try:
            ebitda = excel.evaluate('Summary!B5')
            if base_ebitda is None:
                base_ebitda = ebitda
                change = 0
            else:
                change = ebitda - base_ebitda
            
            print(f"{rate:<15.1%}{ebitda:<15,.0f}{change:>+10,.0f}")
        except:
            print(f"{rate:<15.1%}Error")
    
    return results


def example_3_dependency_analysis():
    """
    Example 3: Dependency Analysis
    
    Demonstrates how to analyze and visualize dependencies
    of critical cells in the model.
    """
    print("\n=== Example 3: Dependency Analysis ===")
    
    excel = create_sample_financial_model()
    
    # Analyze dependencies of a critical cell
    critical_cell = 'Summary!B5'  # EBITDA
    
    print(f"Analyzing dependencies for: {critical_cell}")
    
    # Generate dependency tree
    print("\nDependency Tree:")
    try:
        for line in excel.value_tree_str(critical_cell):
            print(line)
    except Exception as e:
        print(f"Error generating tree: {e}")
    
    # Bidirectional analysis
    print(f"\nBidirectional Analysis for {critical_cell}:")
    
    try:
        # Evaluate to build graph
        excel.evaluate(critical_cell)
        
        target_cell = excel.cell_map.get(critical_cell)
        if target_cell:
            # Precedents (inputs)
            predecessors = list(excel.dep_graph.predecessors(target_cell))
            print(f"Direct precedents ({len(predecessors)}):")
            for pred in predecessors[:5]:  # Show only first 5
                print(f"  ← {pred.address.address}")
            
            # Dependents (outputs)
            successors = list(excel.dep_graph.successors(target_cell))
            print(f"Direct dependents ({len(successors)}):")
            for succ in successors[:5]:  # Show only first 5
                print(f"  → {succ.address.address}")
        else:
            print("Cell not found in graph")
            
    except Exception as e:
        print(f"Error in bidirectional analysis: {e}")
    
    # Export graph for visual analysis
    print("\nExporting graph for visual analysis...")
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            gexf_file = os.path.join(tmpdir, 'dependency_graph.gexf')
            excel.export_to_gexf(gexf_file)
            print(f"Graph exported to: {gexf_file}")
            print("(Can be opened in Gephi for visualization)")
    except Exception as e:
        print(f"Error exporting graph: {e}")


def example_4_model_validation():
    """
    Example 4: Robust Model Validation
    
    Demonstrates different types of validation available
    to ensure model integrity.
    """
    print("\n=== Example 4: Robust Model Validation ===")
    
    excel = create_sample_financial_model()
    
    # Complete model validation
    print("1. Complete model validation...")
    validation_results = excel.validate_calcs()
    
    print(f"Validation results:")
    if not validation_results:
        print("  ✅ All calculations are consistent with Excel")
    else:
        for category, errors in validation_results.items():
            print(f"  ⚠️ {category}: {len(errors)} issues")
            if isinstance(errors, dict):
                for error_type, error_list in errors.items():
                    print(f"    - {error_type}: {len(error_list)} cases")
    
    # Validation of specific cells
    print("\n2. Critical cell validation...")
    critical_cells = ['Summary!B1', 'Summary!B5', 'Summary!B6']  # Revenue, EBITDA, FCF
    
    for cell in critical_cells:
        try:
            cell_validation = excel.validate_calcs(output_addrs=[cell])
            if not cell_validation:
                print(f"  ✅ {cell}: Validated")
            else:
                print(f"  ⚠️ {cell}: Issues detected")
        except Exception as e:
            print(f"  ❌ {cell}: Error - {e}")
    
    # Serialization validation
    print("\n3. Serialization validation...")
    try:
        # Create sub-model for testing
        excel.trim_graph(
            input_addrs=['Assumptions!B1'],  # Revenue_Growth
            output_addrs=['Summary!B1']      # Revenue
        )
        
        serialization_results = excel.validate_serialized(
            output_addrs=['Summary!B1']
        )
        
        if not serialization_results:
            print("  ✅ Serialization consistent")
        else:
            print(f"  ⚠️ Serialization issues: {len(serialization_results)}")
            
    except Exception as e:
        print(f"  ❌ Error in serialization validation: {e}")
    
    # Validation with custom tolerance
    print("\n4. Custom tolerance validation...")
    try:
        tolerance_validation = excel.validate_calcs(
            output_addrs=['Summary!B1'],  # Revenue
            tolerance=0.01  # 1 cent tolerance
        )
        
        if not tolerance_validation:
            print("  ✅ Tolerance validation: Passed")
        else:
            print("  ⚠️ Differences greater than tolerance detected")
            
    except Exception as e:
        print(f"  ❌ Error in tolerance validation: {e}")


def example_5_export_and_documentation():
    """
    Example 5: Export and Documentation
    
    Demonstrates how to export models in different formats
    and generate automatic documentation.
    """
    print("\n=== Example 5: Export and Documentation ===")
    
    excel = create_sample_financial_model()
    
    # Create sub-model for export
    excel.trim_graph(
        input_addrs=['Assumptions!B1', 'Assumptions!B2'],  # Revenue_Growth, COGS_Rate
        output_addrs=['Summary!B5']  # EBITDA
    )
    
    print(f"Model prepared for export: {len(excel.cell_map)} cells")
    
    # Export in multiple formats
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = os.path.join(tmpdir, 'financial_model')
        
        print("\nExporting model in multiple formats:")
        
        # 1. Pickle (fastest)
        try:
            pickle_file = f"{base_path}.pkl"
            excel.to_file(pickle_file)
            size_pkl = os.path.getsize(pickle_file)
            print(f"  ✅ Pickle: {pickle_file} ({size_pkl:,} bytes)")
        except Exception as e:
            print(f"  ❌ Error exporting Pickle: {e}")
        
        # 2. YAML (readable)
        try:
            yaml_file = f"{base_path}.yml"
            excel.to_file(yaml_file)
            size_yml = os.path.getsize(yaml_file)
            print(f"  ✅ YAML: {yaml_file} ({size_yml:,} bytes)")
        except Exception as e:
            print(f"  ❌ Error exporting YAML: {e}")
        
        # 3. JSON (portable)
        try:
            json_file = f"{base_path}.json"
            excel.to_file(json_file)
            size_json = os.path.getsize(json_file)
            print(f"  ✅ JSON: {json_file} ({size_json:,} bytes)")
        except Exception as e:
            print(f"  ❌ Error exporting JSON: {e}")
        
        # 4. GEXF for visualization
        try:
            gexf_file = f"{base_path}.gexf"
            excel.export_to_gexf(gexf_file)
            size_gexf = os.path.getsize(gexf_file)
            print(f"  ✅ GEXF: {gexf_file} ({size_gexf:,} bytes)")
        except Exception as e:
            print(f"  ❌ Error exporting GEXF: {e}")
    
    # Generate dependency documentation
    print("\nGenerating dependency documentation:")
    
    critical_outputs = ['Summary!B5']  # EBITDA
    
    for output in critical_outputs:
        print(f"\n--- Documentation for {output} ---")
        try:
            # Show dependency tree
            tree_lines = list(excel.value_tree_str(output))
            for line in tree_lines[:10]:  # Show only first 10 lines
                print(line)
            
            if len(tree_lines) > 10:
                print(f"... and {len(tree_lines) - 10} more lines")
                
        except Exception as e:
            print(f"Error generating documentation: {e}")
    
    # Model statistics
    print(f"\nModel statistics:")
    print(f"  Total cells: {len(excel.cell_map)}")
    print(f"  Graph nodes: {len(excel.dep_graph.nodes())}")
    print(f"  Graph edges: {len(excel.dep_graph.edges())}")
    
    # Identify cells with most dependencies
    if excel.dep_graph.nodes():
        print(f"\nCells with most dependents:")
        cell_deps = [(cell, len(list(excel.dep_graph.successors(cell)))) 
                     for cell in excel.dep_graph.nodes()]
        cell_deps.sort(key=lambda x: x[1], reverse=True)
        
        for cell, dep_count in cell_deps[:5]:
            print(f"  {cell.address.address}: {dep_count} dependents")


def create_sample_financial_model():
    """
    Creates a sample financial model for demonstration.
    
    In a real case, this would be replaced by:
    return ExcelCompiler('path/to/financial_model.xlsx')
    """
    from openpyxl import Workbook
    
    wb = Workbook()
    
    # Assumptions sheet
    assumptions = wb.create_sheet('Assumptions')
    assumptions['A1'] = 'Revenue_Growth'
    assumptions['B1'] = 0.05  # 5%
    assumptions['A2'] = 'COGS_Rate'
    assumptions['B2'] = 0.60  # 60%
    assumptions['A3'] = 'OpEx_Rate'
    assumptions['B3'] = 0.25  # 25%
    assumptions['A4'] = 'Base_Revenue'
    assumptions['B4'] = 1000000  # $1M
    
    # Summary sheet
    summary = wb.create_sheet('Summary')
    summary['A1'] = 'Revenue'
    summary['B1'] = '=Assumptions!B4*(1+Assumptions!B1)'
    summary['A2'] = 'COGS'
    summary['B2'] = '=B1*Assumptions!B2'
    summary['A3'] = 'Gross_Profit'
    summary['B3'] = '=B1-B2'
    summary['A4'] = 'OpEx'
    summary['B4'] = '=B1*Assumptions!B3'
    summary['A5'] = 'EBITDA'
    summary['B5'] = '=B3-B4'
    summary['A6'] = 'FCF'
    summary['B6'] = '=B5*0.8'  # Simplified FCF
    
    # Remove default sheet
    wb.remove(wb['Sheet'])
    
    return ExcelCompiler(excel=wb)


def main():
    """Runs all examples."""
    print("Model Focusing Examples in Pycel")
    print("=" * 50)
    
    try:
        example_1_financial_model_audit()
        example_2_sensitivity_analysis()
        example_3_dependency_analysis()
        example_4_model_validation()
        example_5_export_and_documentation()
        
        print("\n" + "=" * 50)
        print("✅ All examples executed successfully")
        
    except Exception as e:
        print(f"\n❌ Error executing examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()