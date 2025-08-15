import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

PATHS = {
    'dual_ma': os.path.join(ROOT, 'analysis/backtesting/dual_MA_crossover/ma_crossover_summary.json'),
    'single_ma': os.path.join(ROOT, 'analysis/backtesting/single_MA/ma_summary.json'),
    'rsi': os.path.join(ROOT, 'analysis/backtesting/RSI/rsi_summary.json'),
    'bollinger': os.path.join(ROOT, 'analysis/backtesting/bollinger-bands/bollinger_summary.json'),
}

OUTPUT_PATH = os.path.join(ROOT, 'analysis/backtesting/best_strategies_summary.json')


def load_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, 'r') as f:
        return json.load(f)


def best_by_total_profit(entries, key='total_profit'):
    if not entries:
        return None
    return max(entries, key=lambda x: x.get(key, float('-inf')))


def compute_best():
    results = {}

    # Dual MA crossover
    dual = load_json(PATHS['dual_ma'])
    if dual:
        best_dual = best_by_total_profit(dual, 'total_profit')
        results['dual_ma'] = {
            'best': best_dual,
            'total_configs': len(dual),
        }

    # Single MA
    single = load_json(PATHS['single_ma'])
    if single:
        best_single = best_by_total_profit(single, 'total_profit')
        results['single_ma'] = {
            'best': best_single,
            'total_configs': len(single),
        }

    # RSI
    rsi = load_json(PATHS['rsi'])
    if rsi:
        best_rsi = best_by_total_profit(rsi, 'total_profit')
        results['rsi'] = {
            'best': best_rsi,
            'total_configs': len(rsi),
        }

    # Bollinger
    bb = load_json(PATHS['bollinger'])
    if bb:
        best_bb = best_by_total_profit(bb, 'total_profit')
        results['bollinger'] = {
            'best': best_bb,
            'total_configs': len(bb),
        }

    # Overall best across all strategies by total_profit
    candidates = []
    for strategy, data in results.items():
        best = data.get('best')
        if best:
            candidates.append((strategy, best))
    overall = None
    if candidates:
        strategy, best = max(candidates, key=lambda x: x[1].get('total_profit', float('-inf')))
        overall = {
            'strategy': strategy,
            'config': best,
        }
    results['overall_best_by_total_profit'] = overall
    return results


def main():
    results = compute_best()
    # Print short summary
    print("Best by strategy (total_profit):")
    for strat in ['dual_ma', 'single_ma', 'rsi', 'bollinger']:
        data = results.get(strat)
        if not data:
            continue
        best = data['best']
        tp = best.get('total_profit') if best else None
        print(f"- {strat}: total_configs={data['total_configs']}, best_total_profit={tp}, best={best}")
    print("\nOverall best:")
    print(results.get('overall_best_by_total_profit'))

    # Save JSON
    with open(OUTPUT_PATH, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSaved: {OUTPUT_PATH}")


if __name__ == '__main__':
    main()


