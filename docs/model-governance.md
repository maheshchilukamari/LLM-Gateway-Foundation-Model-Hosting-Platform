# Model Governance

Every model entry should describe:

- Owner.
- Version.
- Approval status.
- Deployment date.
- Task.
- License.
- Source.
- Risk level.
- Supported use cases.
- Restricted use cases.
- Evaluation status.

The sample YAML metadata demonstrates these fields for local development models. Later phases persist governance metadata in PostgreSQL and link each request to the selected model version.

