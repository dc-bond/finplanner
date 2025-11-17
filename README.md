# Finplanner 9000

A comprehensive financial planning application that projects household finances through retirement using deterministic and Monte Carlo modeling.

## How It Works

1. **Setup Your Scenario**: Configure household members, account balances, real estate properties, income sources, and expenses through the web interface
2. **Age-Based Modeling**: The system tracks each person's age and automatically adjusts investment strategies from aggressive to conservative over time
3. **Run Projections**: Generate year-by-year financial projections showing portfolio growth, cash flow, and net worth
4. **Analyze Results**: View deterministic projections and Monte Carlo simulations with confidence intervals and success rates

## Notable Features

- **Multi-Person Households**: Track different retirement ages and person-specific income/expenses for couples and families
- **Investment Modeling**: Age-based transitions from aggressive to conservative growth rates with account-specific strategies
- **Real Estate Integration**: Model existing properties and future purchases with mortgage calculations, appreciation, and equity tracking
- **Monte Carlo Simulations**: Stochastic analysis with correlated market returns and confidence bands

## Technology Stack

- **Python 3** with scientific computing libraries (NumPy, Pandas, SciPy)
- **Streamlit** for the web interface
- **Matplotlib** for financial charts and visualizations
- **Nix** for reproducible development environment and/or deployment
- **Docker** for containerized deployment

## Installation

### Option 1: Docker

Build and run using Docker:

```bash
# Clone the repository
git clone https://github.com/dc-bond/finplanner.git
cd finplanner

# Build the Docker image
docker build -t finplanner .

# Run the container
docker run -p 8501:8501 finplanner
```

The application will be available at http://localhost:8501

### Option 2: Nix Flake

#### For Development

```bash
# Clone the repository
git clone https://github.com/dc-bond/finplanner.git
cd finplanner

# Enter development environment
nix develop

# Run the application
streamlit run app.py
```

#### For Deployment

```bash
# Install and run directly
nix run github:dc-bond/finplanner

# Or build and install
nix build github:dc-bond/finplanner
./result/bin/finplanner
```

#### NixOS Service

Add to your NixOS configuration:

```nix
{
  inputs.finplanner.url = "github:dc-bond/finplanner";
  
  outputs = { self, nixpkgs, finplanner }: {
    nixosConfigurations.your-host = nixpkgs.lib.nixosSystem {
      modules = [
        finplanner.nixosModules.default
        {
          services.finplanner = {
            enable = true;
            port = 8501;
            address = "0.0.0.0";  # for external access
          };
        }
      ];
    };
  };
}
```

Then rebuild your system:
```bash
sudo nixos-rebuild switch
```

## Usage

Launch the application and navigate through the tabs:

1. **Scenario Setup**: Configure household people, accounts, real estate, income, and expenses
2. **Account Balances**: View portfolio growth and real estate equity projections
3. **Cash Flow**: Analyze income vs expenses over time
4. **Monte Carlo**: Explore probabilistic outcomes with confidence intervals

## Important Disclaimer

⚠️ **BETA SOFTWARE - USE AT YOUR OWN RISK** ⚠️

**This application is currently in beta status and should not be relied upon as financial advice.**

- **Not Financial Advice**: This tool provides projections and estimates for educational purposes only. It is not intended to provide financial, investment, tax, or legal advice.
- **Verify All Calculations**: Users are responsible for verifying all calculations and assumptions. The software may contain bugs or produce incorrect results.
- **Consult Professionals**: Always consult with qualified financial advisors, tax professionals, and legal counsel before making significant financial decisions.
- **No Guarantee of Accuracy**: Past performance does not guarantee future results. Market conditions, tax laws, and personal circumstances can significantly impact actual outcomes.
- **Beta Status**: This software is under active development and may contain errors, incomplete features, or unexpected behavior.
- **User Responsibility**: By using this application, you acknowledge that you are solely responsible for any financial decisions you make based on its output.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.