#!/usr/bin/env python3
"""
Create Visual Demonstration of Git-Based Taxonomy

Shows how git diff visualization would help researchers understand
the Caudovirales reorganization.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, Rectangle
import numpy as np

def create_before_after_visualization():
    """Create a before/after visualization of the reorganization."""
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 10))
    
    # Before (2021)
    ax1.set_title("BEFORE: Traditional Morphology-Based (1971-2021)", fontsize=16, weight='bold')
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 10)
    ax1.axis('off')
    
    # Order Caudovirales
    order_box = FancyBboxPatch((1, 7), 8, 2, 
                               boxstyle="round,pad=0.1",
                               facecolor='lightblue',
                               edgecolor='darkblue',
                               linewidth=2)
    ax1.add_patch(order_box)
    ax1.text(5, 8, "Order: Caudovirales", ha='center', va='center', fontsize=14, weight='bold')
    ax1.text(5, 7.3, "3,452 tailed phage species", ha='center', va='center', fontsize=10)
    
    # Three families
    families = [
        ("Myoviridae", "Contractile tails", 1088, 'lightcoral'),
        ("Siphoviridae", "Long flexible tails", 1847, 'lightgreen'),
        ("Podoviridae", "Short tails", 517, 'lightyellow')
    ]
    
    x_positions = [2, 5, 8]
    for i, (family, desc, count, color) in enumerate(families):
        family_box = FancyBboxPatch((x_positions[i]-1.2, 3), 2.4, 3,
                                   boxstyle="round,pad=0.1",
                                   facecolor=color,
                                   edgecolor='black',
                                   linewidth=1)
        ax1.add_patch(family_box)
        ax1.text(x_positions[i], 5.5, family, ha='center', va='center', fontsize=12, weight='bold')
        ax1.text(x_positions[i], 4.8, desc, ha='center', va='center', fontsize=9)
        ax1.text(x_positions[i], 4.2, f"{count} species", ha='center', va='center', fontsize=9)
        
        # Connection line
        ax1.plot([5, x_positions[i]], [7, 6], 'k-', linewidth=1)
    
    # Classification basis
    ax1.text(5, 1, "Classification: Electron microscopy morphology", 
             ha='center', va='center', fontsize=11, style='italic',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='wheat'))
    
    # After (2021+)
    ax2.set_title("AFTER: Genomic-Based Classification (2021+)", fontsize=16, weight='bold')
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 10)
    ax2.axis('off')
    
    # Class Caudoviricetes
    class_box = FancyBboxPatch((1, 7), 8, 2,
                              boxstyle="round,pad=0.1",
                              facecolor='lavender',
                              edgecolor='purple',
                              linewidth=2)
    ax2.add_patch(class_box)
    ax2.text(5, 8, "Class: Caudoviricetes", ha='center', va='center', fontsize=14, weight='bold')
    ax2.text(5, 7.3, "3,452 species (22+ families)", ha='center', va='center', fontsize=10)
    
    # Sample of new families
    new_families = [
        ("From Myoviridae", ["Straboviridae", "Herelleviridae", "Kyanoviridae"], 'lightcoral'),
        ("From Siphoviridae", ["Drexlerviridae", "Demerecviridae", "Siphoviridae s.s."], 'lightgreen'),
        ("From Podoviridae", ["Salasmaviridae", "Schitoviridae", "Autographiviridae"], 'lightyellow')
    ]
    
    y_start = 5.5
    for origin, families, color in new_families:
        ax2.text(1.5, y_start, origin + ":", fontsize=10, weight='bold')
        for j, family in enumerate(families):
            family_box = FancyBboxPatch((3 + j*2, y_start-0.4), 1.8, 0.7,
                                       boxstyle="round,pad=0.05",
                                       facecolor=color,
                                       edgecolor='gray',
                                       linewidth=0.5,
                                       alpha=0.7)
            ax2.add_patch(family_box)
            ax2.text(3.9 + j*2, y_start, family, ha='center', va='center', fontsize=8)
        y_start -= 1.5
    
    # Classification basis
    ax2.text(5, 1, "Classification: Whole genome phylogeny + protein analysis", 
             ha='center', va='center', fontsize=11, style='italic',
             bbox=dict(boxstyle="round,pad=0.3", facecolor='lightgreen'))
    
    # Add "OBSOLETE" stamps
    for x_pos in x_positions:
        ax1.text(x_pos, 3.5, "OBSOLETE", ha='center', va='center', 
                fontsize=16, weight='bold', color='red', alpha=0.3,
                rotation=30)
    
    plt.suptitle("Caudovirales Reorganization: Impact Visualization", fontsize=20, weight='bold')
    plt.tight_layout()
    plt.savefig('caudovirales_reorganization_visual.png', dpi=300, bbox_inches='tight')
    plt.savefig('caudovirales_reorganization_visual.pdf', bbox_inches='tight')
    print("✅ Created visualization: caudovirales_reorganization_visual.png/.pdf")


def create_git_workflow_diagram():
    """Create diagram showing git workflow benefits."""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # Title
    ax.text(7, 9.5, "Git-Based Taxonomy Workflow", fontsize=20, weight='bold', ha='center')
    
    # Main branch
    ax.plot([1, 13], [7, 7], 'k-', linewidth=3)
    ax.text(0.5, 7, "master", fontsize=12, weight='bold', ha='right')
    
    # Commits on main
    commits_main = [
        (2, "Initial\nstructure", "v0.1.0"),
        (4, "Traditional\nCaudovirales", "MSL34"),
        (11, "Post-\nreorganization", "MSL35"),
        (13, "Current", None)
    ]
    
    for x, label, tag in commits_main:
        ax.plot(x, 7, 'ko', markersize=12)
        ax.text(x, 6.5, label, ha='center', va='top', fontsize=9)
        if tag:
            ax.add_patch(Rectangle((x-0.4, 7.2), 0.8, 0.4, 
                                 facecolor='yellow', edgecolor='black'))
            ax.text(x, 7.4, tag, ha='center', va='center', fontsize=8)
    
    # Proposal branch
    ax.plot([4, 6, 8, 10, 11], [7, 5, 5, 5, 7], 'b-', linewidth=2)
    ax.text(5.5, 4.5, "proposal/2021-caudovirales", fontsize=10, color='blue')
    
    # Commits on proposal branch
    commits_branch = [
        (6, "Add\nproposal"),
        (8, "Implement\nchanges"),
        (10, "Test &\nvalidate")
    ]
    
    for x, label in commits_branch:
        ax.plot(x, 5, 'bo', markersize=10)
        ax.text(x, 4.5, label, ha='center', va='top', fontsize=8)
    
    # Benefits boxes
    benefits = [
        (2, 2.5, "Version Control", "Check out any\nhistorical state"),
        (5, 2.5, "Branching", "Develop proposals\nseparately"),
        (8, 2.5, "Transparency", "See all changes\nand rationale"),
        (11, 2.5, "Revertibility", "Can undo if\nproblems found")
    ]
    
    for x, y, title, desc in benefits:
        box = FancyBboxPatch((x-1, y-0.7), 2, 1.4,
                           boxstyle="round,pad=0.1",
                           facecolor='lightblue',
                           edgecolor='darkblue',
                           linewidth=1)
        ax.add_patch(box)
        ax.text(x, y+0.3, title, ha='center', va='center', fontsize=10, weight='bold')
        ax.text(x, y-0.3, desc, ha='center', va='center', fontsize=8)
    
    # Commands examples
    ax.text(7, 1, "Example Git Commands:", fontsize=12, weight='bold', ha='center')
    commands = [
        "git checkout MSL34  # View pre-2021 taxonomy",
        "git diff MSL34..MSL35  # See what changed",
        "git log --graph  # View history",
        "git blame families/straboviridae/family.yaml  # Who created this?"
    ]
    
    for i, cmd in enumerate(commands):
        ax.text(7, 0.5-i*0.2, cmd, fontsize=9, ha='center', 
               fontfamily='monospace', style='italic')
    
    plt.savefig('git_workflow_benefits.png', dpi=300, bbox_inches='tight')
    plt.savefig('git_workflow_benefits.pdf', bbox_inches='tight')
    print("✅ Created workflow diagram: git_workflow_benefits.png/.pdf")


def create_migration_example():
    """Show how git helps with migration between versions."""
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    ax.text(6, 7.5, "Automated Migration with Git", fontsize=18, weight='bold', ha='center')
    
    # Old classification
    old_box = FancyBboxPatch((0.5, 4), 5, 2.5,
                            boxstyle="round,pad=0.1",
                            facecolor='#ffcccc',
                            edgecolor='darkred',
                            linewidth=2)
    ax.add_patch(old_box)
    ax.text(3, 5.8, "Your Data (MSL34)", fontsize=12, weight='bold', ha='center')
    ax.text(3, 5.3, "Species: Escherichia virus T4", fontsize=10, ha='center')
    ax.text(3, 4.8, "Family: Myoviridae", fontsize=10, ha='center')
    ax.text(3, 4.3, "Order: Caudovirales", fontsize=10, ha='center')
    
    # Arrow
    arrow = patches.FancyArrowPatch((5.5, 5.25), (6.5, 5.25),
                                   connectionstyle="arc3,rad=0", 
                                   arrowstyle='-|>',
                                   mutation_scale=20,
                                   linewidth=3,
                                   color='green')
    ax.add_patch(arrow)
    ax.text(6, 5.8, "git-taxonomy\nmigrate", ha='center', va='center', 
           fontsize=10, weight='bold', color='green')
    
    # New classification
    new_box = FancyBboxPatch((6.5, 4), 5, 2.5,
                            boxstyle="round,pad=0.1",
                            facecolor='#ccffcc',
                            edgecolor='darkgreen',
                            linewidth=2)
    ax.add_patch(new_box)
    ax.text(9, 5.8, "Your Data (MSL35)", fontsize=12, weight='bold', ha='center')
    ax.text(9, 5.3, "Species: Escherichia virus T4", fontsize=10, ha='center')
    ax.text(9, 4.8, "Family: Straboviridae", fontsize=10, ha='center', color='green')
    ax.text(9, 4.3, "Class: Caudoviricetes", fontsize=10, ha='center', color='green')
    
    # Mapping info
    mapping_box = FancyBboxPatch((2, 1), 8, 2,
                                boxstyle="round,pad=0.1",
                                facecolor='lightyellow',
                                edgecolor='orange',
                                linewidth=1)
    ax.add_patch(mapping_box)
    ax.text(6, 2.5, "TAXONOMY_MAPPING_2021.yaml", fontsize=11, weight='bold', ha='center')
    ax.text(6, 2, "Myoviridae → Straboviridae (T4-like viruses)", fontsize=9, ha='center')
    ax.text(6, 1.6, "Based on: Large terminase phylogeny", fontsize=9, ha='center', style='italic')
    ax.text(6, 1.2, "Confidence: High (bootstrap >95%)", fontsize=9, ha='center')
    
    plt.savefig('git_migration_example.png', dpi=300, bbox_inches='tight')
    plt.savefig('git_migration_example.pdf', bbox_inches='tight')
    print("✅ Created migration example: git_migration_example.png/.pdf")


if __name__ == "__main__":
    print("Creating visual demonstrations...")
    create_before_after_visualization()
    create_git_workflow_diagram()
    create_migration_example()
    print("\n✅ All visualizations created successfully!")