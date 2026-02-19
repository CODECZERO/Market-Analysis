#!/usr/bin/env python3
"""
Trading Tools Hub - Unified interface for all trading features
"""

import argparse
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich import box

# Import our tools
from performance_tracker import (
    calculate_performance_stats, 
    get_recent_recommendations, 
    export_to_csv
)
from alert_system import AlertSystem
from backtest import PortfolioBacktester
from datetime import datetime, timedelta

console = Console()

def show_performance_stats():
    """Display performance tracking statistics"""
    console.print("\n[bold cyan]📊 PERFORMANCE STATISTICS[/bold cyan]\n")
    
    stats = calculate_performance_stats()
    
    table = Table(box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green", justify="right")
    
    table.add_row("Total Recommendations", str(stats.get('total_recommendations', 0)))
    table.add_row("Active Positions", str(stats.get('active_recommendations', 0)))
    table.add_row("Closed Positions", str(stats.get('closed_positions', 0)))
    table.add_row("Successful Trades", str(stats.get('successful_trades', 0)))
    table.add_row("Failed Trades", str(stats.get('failed_trades', 0)))
    table.add_row("Success Rate", f"{stats.get('success_rate', 0):.1f}%")
    table.add_row("Avg Return", f"{stats.get('avg_return', 0):.2f}%")
    table.add_row("Best Return", f"{stats.get('best_return', 0):.2f}%")
    table.add_row("Worst Return", f"{stats.get('worst_return', 0):.2f}%")
    table.add_row("Total Return", f"{stats.get('total_return', 0):.2f}%")
    
    console.print(table)
    
    # Show recent recommendations
    console.print("\n[bold yellow]📝 Recent Recommendations:[/bold yellow]\n")
    recent = get_recent_recommendations(5)
    
    if recent:
        rec_table = Table(box=box.SIMPLE)
        rec_table.add_column("Date", style="dim")
        rec_table.add_column("Symbol")
        rec_table.add_column("Action")
        rec_table.add_column("Status")
        
        for rec in recent:
            rec_table.add_row(
                rec['timestamp'][:10],
                rec['symbol'],
                rec.get('action', 'N/A'),
                rec.get('status', 'active')
            )
        
        console.print(rec_table)
    else:
        console.print("[dim]No recommendations yet[/dim]")

def manage_alerts():
    """Manage price and technical alerts"""
    console.print("\n[bold cyan]🔔 ALERT MANAGEMENT[/bold cyan]\n")
    
    alerts = AlertSystem()
    
    while True:
        console.print("\n[1] Add Price Alert")
        console.print("[2] Add RSI Alert")
        console.print("[3] Check Active Alerts")
        console.print("[4] Check Triggered Alerts")
        console.print("[5] Remove Alert")
        console.print("[6] Back to Main Menu\n")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            symbol = Prompt.ask("Stock symbol (e.g., TCS.NS)")
            if not symbol.endswith('.NS'):
                symbol += '.NS'
            price = float(Prompt.ask("Target price"))
            condition = Prompt.ask("Condition", choices=["above", "below"])
            alerts.add_price_alert(symbol, price, condition)
        
        elif choice == "2":
            symbol = Prompt.ask("Stock symbol (e.g., TCS.NS)")
            if not symbol.endswith('.NS'):
                symbol += '.NS'
            rsi = float(Prompt.ask("RSI threshold (e.g., 70 for overbought, 30 for oversold)"))
            condition = Prompt.ask("Condition", choices=["above", "below"])
            alerts.add_rsi_alert(symbol, rsi, condition)
        
        elif choice == "3":
            active = alerts.get_active_alerts()
            if active:
                console.print(f"\n✅ {len(active)} active alerts:")
                for a in active:
                    if a['type'] == 'price':
                        console.print(f"  • {a['symbol']}: Price {a['condition']} ₹{a['target_price']:,.2f}")
                    else:
                        console.print(f"  • {a['symbol']}: RSI {a['condition']} {a['rsi_threshold']}")
            else:
                console.print("[dim]No active alerts[/dim]")
        
        elif choice == "4":
            console.print("\n[yellow]Checking alerts...[/yellow]")
            triggered = alerts.check_alerts()
            if triggered:
                console.print(f"\n🔔 {len(triggered)} alerts triggered!")
                alerts.show_triggered_alerts()
            else:
                console.print("[dim]No triggered alerts[/dim]")
        
        elif choice == "5":
            alert_id = int(Prompt.ask("Alert ID to remove"))
            alerts.remove_alert(alert_id)
        
        else:
            break

def run_backtest():
    """Run portfolio backtest"""
    console.print("\n[bold cyan]📈 PORTFOLIO BACKTESTING[/bold cyan]\n")
    
    # Get parameters
    capital = float(Prompt.ask("Initial capital", default="100000"))
    days = int(Prompt.ask("Backtest period (days)", default="180"))
    
    symbols = ["TCS.NS", "RELIANCE.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
    
    console.print(f"\n[yellow]Running backtest on {len(symbols)} stocks...[/yellow]")
    console.print("[dim]This may take a minute...[/dim]\n")
    
    # Run backtest
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    
    backtester = PortfolioBacktester(initial_capital=capital)
    results = backtester.backtest_strategy(symbols, start_date, end_date)
    backtester.print_results(results)
    
    # Ask to export
    if Confirm.ask("\nExport trade history to CSV?"):
        backtester.export_trades_to_csv()

def export_data():
    """Export data to CSV"""
    console.print("\n[bold cyan]📥 EXPORT DATA[/bold cyan]\n")
    
    console.print("[1] Export Recommendations")
    console.print("[2] Export Alert History")
    console.print("[3] Export All Data\n")
    
    choice = Prompt.ask("Select", choices=["1", "2", "3"])
    
    if choice in ["1", "3"]:
        export_to_csv()
    
    console.print("\n✅ Export complete!")

def main_menu():
    """Main menu for trading tools"""
    while True:
        console.clear()
        console.print("\n[bold green]═" * 40 + "[/bold green]")
        console.print("[bold cyan]🛠️  TRADING TOOLS HUB[/bold cyan]")
        console.print("[bold green]═" * 40 + "[/bold green]\n")
        
        console.print("[1] 📊 View Performance Stats")
        console.print("[2] 🔔 Manage Alerts")
        console.print("[3] 📈 Run Backtest")
        console.print("[4] 📥 Export Data")
        console.print("[5] 🔄 Run Advanced Dashboard")
        console.print("[6] ❌ Exit\n")
        
        choice = Prompt.ask("Select tool", choices=["1", "2", "3", "4", "5", "6"])
        
        if choice == "1":
            show_performance_stats()
            Prompt.ask("\nPress Enter to continue")
        elif choice == "2":
            manage_alerts()
        elif choice == "3":
            run_backtest()
            Prompt.ask("\nPress Enter to continue")
        elif choice == "4":
            export_data()
            Prompt.ask("\nPress Enter to continue")
        elif choice == "5":
            # Run advanced dashboard
            import advanced_cli
            advanced_cli.interactive_menu()
        else:
            console.print("\n[green]✅ Goodbye![/green]")
            break

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Trading Tools Hub")
    parser.add_argument('--stats', action='store_true', help='Show performance stats')
    parser.add_argument('--alerts', action='store_true', help='Manage alerts')
    parser.add_argument('--backtest', action='store_true', help='Run backtest')
    parser.add_argument('--export', action='store_true', help='Export data')
    
    args = parser.parse_args()
    
    if args.stats:
        show_performance_stats()
    elif args.alerts:
        manage_alerts()
    elif args.backtest:
        run_backtest()
    elif args.export:
        export_data()
    else:
        main_menu()
