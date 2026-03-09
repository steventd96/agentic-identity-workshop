# Agentic Security Hands-On Lab - Notebooks

This hands-on lab is divided into multiple Jupyter notebooks for easier navigation and completion. Each notebook focuses on a specific aspect of agentic security.

## 📚 Lab Structure

### Part 1: Introduction and Setup (30 minutes)
**Notebook:** `01-introduction-and-setup.ipynb`
- Learning objectives and core concepts
- OAuth 2.0 Token Exchange explained
- Architecture overview
- Environment setup and verification
- Start infrastructure services

### Part 2: Vault Configuration (20 minutes)
**Notebook:** `02-vault-configuration.ipynb`
- Configure HashiCorp Vault
- Set up JWT authentication
- Configure database secrets engine
- Create and understand policies
- Set up external group mapping

### Part 3: Langflow Setup (30 minutes)
**Notebook:** `03-langflow-setup.ipynb`
- Install custom Langflow components
- Set up Langflow environment
- Configure Langflow tools
- Prepare for agent integration

### Part 4: Demo Application Walkthrough (30-40 minutes)
**Notebook:** `04-demo-app-walkthrough.ipynb`
- Import and configure the HR Agent flow
- Test with different user roles (hr-basic, hr-admin)
- Run end-to-end access control scenarios
- Test OAuth token exchange
- Authenticate with Vault using JWT
- Generate dynamic database credentials
- Observe complete security flow with audit logs
- Optional: Run the frontend application

## 🚀 Getting Started

1. **Prerequisites:**
   - Podman running
   - Python 3.9+
   - Configured `.env` file

2. **Start in Order:**
   - Begin with notebook 01
   - Complete notebooks 01-04 for the complete lab experience
   - Follow the notebooks sequentially for best results

3. **Estimated Total Time:**
   - Complete Lab (Notebooks 1-4): 110-130 minutes

## 📝 Notes

- Each notebook is self-contained with its own explanations
- Code cells should be run in order
- Variables are passed between notebooks using Python modules
- You can restart from any notebook if needed

## 🆘 Need Help?

- Check the main `README.md` in the lab root directory
- Review the architecture diagrams in notebook 01
- Ensure all services are running with `podman-compose ps`

---

**Ready to start?** Open `01-introduction-and-setup.ipynb` and begin your journey into agentic security!