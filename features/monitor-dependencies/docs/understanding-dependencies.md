# Understanding notification dependencies

A dependency in this module answers an operational question:

> If this monitor reports a failure, which upstream dependency observations should gate its failure notification?

Each monitor keeps its independently observed health. Configuring a dependency does not manufacture a DOWN result, change heartbeat history or uptime, or prove that the dependency caused an outage. The relationship controls failure notifications; it is not a declaration that a child's health must always equal its parent's health.

## Strict dependencies and apparently contradictory health

For a strict dependency, the expectation is straightforward. If a service runs only on one host and that host is genuinely unavailable, the service cannot remain available through that host. If the checks measured the relevant functions from the same perspective at the same instant, both would report the loss of availability.

An UP service alongside a DOWN host therefore deserves interpretation. It can reflect different observation times, different definitions of availability, or an incomplete dependency model. Persistent disagreement in a genuinely strict relationship is a reason to investigate the checks and assumptions, rather than automatically dismissing either observation.

## Practical reasons a dependent monitor can be UP

| Situation | What the observations mean | How to interpret the dependency |
| --- | --- | --- |
| Different check times | The service passed its last check; the host then failed and its next check detected that first. The service has not checked again yet. | This temporary disagreement is compatible with a real strict dependency. Neither monitor needs to be defective. Checks are observations, not a synchronized statement of the whole system. |
| Different meanings of availability | A host's ping check fails while its HTTPS services still respond because ICMP is blocked or deprioritized. | The ping check establishes lack of a ping response, not necessarily loss of the host. It can be an accurate ICMP check but an imperfect proxy for the availability required by those services. |
| Redundancy or failover | One host fails, but the service continues on another host. | Both observations can be correct. The service is not strictly dependent on that individual host; its real availability dependency is the hosting pool or other redundant capability. This module's single direct dependency does not model arbitrary AND/OR dependency graphs. |
| Partial functionality or caching | A database is DOWN while a service can still return cached results or serve read-only requests. | An UP check may correctly represent that limited functionality. If it is meant to prove that all business functions work, it is too shallow for that purpose. |

The distinction is often between an imperfect monitor and an imperfect interpretation of what the monitor proves. A successful TCP connection can be a useful, accurate TCP check while being insufficient evidence that the complete application is functioning.

## Reading a dependency chain

Consider this configured chain, where each arrow means "depends on":

`Website → Gateway → Router`

Website depends directly on Gateway. When Website is DOWN, failure notification decisions inspect the entire ancestor chain. Gateway can have a current UP observation while Router has a DOWN observation; the active DOWN Router can still suppress Website's failure alerts. Showing only the configured direct dependency would miss the observation actually blocking those alerts.

The configured dependency and the current blocker therefore have different meanings:

- **Configured dependency:** the direct relationship saved on the monitor, such as Gateway for Website. It exists whether monitors are healthy or unhealthy.
- **Current blocker:** the closest active ancestor with an accepted DOWN observation under the existing suppression rules, such as Router when Gateway is UP. It can change as observations or configuration change.

An UP child remains UP even if an ancestor is DOWN. When the child is DOWN, suppression affects its failure alerts while the child still contributes to the actual DOWN status/counts. Unknown or PENDING ancestors can defer a new failure notification without establishing a confirmed DOWN blocker. Paused and maintenance ancestors are not blockers merely because of those states; their own ancestors are still evaluated. See the [notification gate documentation](0002-notification-gate.md) for complete incident, repeat and recovery semantics.

A label such as "Failure alerts suppressed by Router" explains the notification decision. It does not establish Router as the proven physical root cause of Website's failure.

## Choosing useful checks and relationships

- Decide what UP means for each check: process reachable, protocol responding, a specific function usable, or the complete service available.
- Choose a dependency check that represents the capability its children actually require. A device name alone does not make its probe a complete measure of device availability.
- Account for different polling intervals, retries, check locations and network paths before treating short-lived disagreement as a defect.
- Represent redundancy through an appropriate logical service/pool monitor rather than assuming one optional host is an unavoidable dependency. Any such pool check must itself measure the intended availability policy.
- Investigate persistent contradictions in a strict relationship. Review check coverage, cached responses, failover and the configured chain.
- Preserve independently observed health so these discrepancies remain visible and useful for diagnosis.

Test fixtures may deliberately produce independent failures to exercise suppression, stale-observation and recovery behavior. Those scenarios demonstrate the notification rules; they do not establish that the named monitors have the same strict physical dependencies as real devices or services.

This guide describes the existing notification-dependency model. It does not introduce health propagation or change suppression, incident recovery or browser-toast behavior.
