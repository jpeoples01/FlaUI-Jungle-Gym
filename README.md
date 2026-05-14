# FlaUI-Jungle-Gym

## Overview
FlaUI Jungle Gym is a demonstration project designed to showcase the value of UI test automation in a structured and repeatable way.

This project combines a purpose-built desktop application with an automation framework to demonstrate how testing can be:

- Faster
- More reliable
- Repeatable
- Integrated into CI/CD pipelines

---

## Project Objectives

The goal of this project is to:

- Build a **testable desktop application** (WPF)
- Demonstrate **UI automation using FlaUI**
- Showcase **end-to-end automated test execution**
- Provide a **safe sandbox environment** for experimentation
- Highlight **best practices for automation-friendly design**

# Jungle Gym App

This application is intentionally designed to include a variety of features to support automation testing:

- Login system
- Data entry forms
- Test execution workflows
- Error/edge case scenarios
- File export functionality (planned)


# Suggested Flow for the demonstration

[ Application Under Test (Desktop App) ]
                ↓
        FlaUI / UI Automation
                ↓
          Python Test Layer
                ↓
          Test Reporting (Allure / HTML)
                ↓
        CI/CD Pipeline (GitHub Actions / Azure DevOps)

# Installations Required
- Python v3.11.9
- Pytest
- flaui-uiautomation-wrapper
- venv with Python v3.11.9 Intepreter
- Pyinstaller to build executable file