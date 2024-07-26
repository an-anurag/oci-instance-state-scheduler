OCI Instance State Scheduler
-----------------------------------------------------------

What is this?
------------------------------------------------------------
This is a repository for managing the scheduling of Oracle Cloud Infrastructure (OCI) instances. It provides a set of scripts and configuration files to automate the start and stop of OCI instances based on a predefined schedule.

You can deploy as a standalone automation or OCI function

To get started, follow the steps below:

1. Clone the repository:
    ```
    git clone https://github.com/an-anurag/projects/oci-instance-scheduler.git
    ```

2. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

4. Run the scheduler:
    ```
    python func.py
    ```

    The scheduler will automatically start and stop instances based on the defined schedule.


For more information, refer to the [documentation](https://github.com/an-anurag/oci-instance-state-scheduler/blob/main/docs/README.md).

Feel free to contribute to this project by submitting pull requests or reporting issues on the [GitHub repository](https://github.com/an-anurag/oci-instance-state-scheduler).
