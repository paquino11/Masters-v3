/*
 * Copyright (c) 2019 Contributors to the Eclipse Foundation
 *
 * See the NOTICE file(s) distributed with this work for additional
 * information regarding copyright ownership.
 *
 * This program and the accompanying materials are made available under the
 * terms of the Eclipse Public License 2.0 which is available at
 * http://www.eclipse.org/legal/epl-2.0
 *
 * SPDX-License-Identifier: EPL-2.0
 */
package org.eclipse.ditto.policies.service.persistence.actors.strategies.commands;

import static org.eclipse.ditto.base.model.common.ConditionChecker.checkNotNull;

import java.util.List;
import java.util.Optional;
import java.util.stream.Collectors;

import javax.annotation.Nullable;

import org.eclipse.ditto.json.JsonObject;
import org.eclipse.ditto.base.model.entity.metadata.Metadata;
import org.eclipse.ditto.base.model.headers.DittoHeaders;
import org.eclipse.ditto.base.model.headers.WithDittoHeaders;
import org.eclipse.ditto.base.model.headers.entitytag.EntityTag;
import org.eclipse.ditto.policies.model.Label;
import org.eclipse.ditto.policies.model.Policy;
import org.eclipse.ditto.policies.model.PolicyEntry;
import org.eclipse.ditto.policies.model.PolicyId;
import org.eclipse.ditto.policies.model.PolicyTooLargeException;
import org.eclipse.ditto.policies.model.Resource;
import org.eclipse.ditto.policies.model.ResourceKey;
import org.eclipse.ditto.policies.model.Resources;
import org.eclipse.ditto.policies.api.PoliciesValidator;
import org.eclipse.ditto.policies.service.common.config.PolicyConfig;
import org.eclipse.ditto.internal.utils.persistentactors.results.Result;
import org.eclipse.ditto.internal.utils.persistentactors.results.ResultFactory;
import org.eclipse.ditto.policies.model.signals.commands.PolicyCommandSizeValidator;
import org.eclipse.ditto.policies.model.signals.commands.modify.ModifyResources;
import org.eclipse.ditto.policies.model.signals.commands.modify.ModifyResourcesResponse;
import org.eclipse.ditto.policies.model.signals.events.PolicyEvent;
import org.eclipse.ditto.policies.model.signals.events.ResourcesModified;

/**
 * This strategy handles the {@link org.eclipse.ditto.policies.model.signals.commands.modify.ModifyResources} command.
 */
final class ModifyResourcesStrategy extends AbstractPolicyCommandStrategy<ModifyResources, PolicyEvent<?>> {

    ModifyResourcesStrategy(final PolicyConfig policyConfig) {
        super(ModifyResources.class, policyConfig);
    }

    @Override
    protected Result<PolicyEvent<?>> doApply(final Context<PolicyId> context,
            @Nullable final Policy policy,
            final long nextRevision,
            final ModifyResources command,
            @Nullable final Metadata metadata) {

        final Policy nonNullPolicy = checkNotNull(policy, "policy");
        final PolicyId policyId = context.getState();
        final Label label = command.getLabel();
        final Resources resources = command.getResources();
        final DittoHeaders dittoHeaders = command.getDittoHeaders();

        final List<ResourceKey> rks = resources.stream()
                .map(Resource::getResourceKey)
                .collect(Collectors.toList());
        Policy tmpPolicy = nonNullPolicy;
        for (final ResourceKey rk : rks) {
            tmpPolicy = tmpPolicy.removeResourceFor(label, rk);
        }
        final JsonObject tmpPolicyJsonObject = tmpPolicy.toJson();
        final JsonObject resourceJsonObject = resources.toJson();

        try {
            PolicyCommandSizeValidator.getInstance().ensureValidSize(
                    () -> {
                        final long policyLength = tmpPolicyJsonObject.getUpperBoundForStringSize();
                        final long resourcesLength = resourceJsonObject.getUpperBoundForStringSize() + 5L;
                        return policyLength + resourcesLength;
                    },
                    () -> {
                        final long policyLength = tmpPolicyJsonObject.toString().length();
                        final long resourcesLength = resourceJsonObject.toString().length() + 5L;
                        return policyLength + resourcesLength;
                    },
                    command::getDittoHeaders);
        } catch (final PolicyTooLargeException e) {
            return ResultFactory.newErrorResult(e, command);
        }

        if (nonNullPolicy.getEntryFor(label).isPresent()) {
            final PoliciesValidator validator =
                    PoliciesValidator.newInstance(nonNullPolicy.setResourcesFor(label, resources));

            if (validator.isValid()) {
                final ResourcesModified event =
                        ResourcesModified.of(policyId, label, resources, nextRevision, getEventTimestamp(),
                                dittoHeaders, metadata);
                final WithDittoHeaders response = appendETagHeaderIfProvided(command,
                        ModifyResourcesResponse.of(policyId, label, dittoHeaders), policy);
                return ResultFactory.newMutationResult(command, event, response);
            } else {
                return ResultFactory.newErrorResult(
                        policyEntryInvalid(policyId, label, validator.getReason().orElse(null), dittoHeaders), command);
            }
        } else {
            return ResultFactory.newErrorResult(policyEntryNotFound(policyId, label, dittoHeaders), command);
        }
    }

    @Override
    public Optional<EntityTag> previousEntityTag(final ModifyResources command, @Nullable final Policy previousEntity) {
        return Optional.ofNullable(previousEntity)
                .flatMap(p -> p.getEntryFor(command.getLabel()))
                .map(PolicyEntry::getResources)
                .flatMap(EntityTag::fromEntity);
    }

    @Override
    public Optional<EntityTag> nextEntityTag(final ModifyResources command, @Nullable final Policy newEntity) {
        return Optional.of(command.getResources()).flatMap(EntityTag::fromEntity);
    }
}
