/*
 * Copyright (c) 2017 Contributors to the Eclipse Foundation
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
package org.eclipse.ditto.things.service.persistence.actors;

import javax.annotation.Nullable;

import org.eclipse.ditto.base.model.acks.DittoAcknowledgementLabel;
import org.eclipse.ditto.base.model.exceptions.DittoRuntimeExceptionBuilder;
import org.eclipse.ditto.base.model.headers.DittoHeaders;
import org.eclipse.ditto.base.model.headers.LiveChannelTimeoutStrategy;
import org.eclipse.ditto.base.model.headers.WithDittoHeaders;
import org.eclipse.ditto.base.model.json.JsonSchemaVersion;
import org.eclipse.ditto.base.model.signals.commands.Command;
import org.eclipse.ditto.internal.utils.config.DefaultScopedConfig;
import org.eclipse.ditto.internal.utils.persistence.mongo.config.ActivityCheckConfig;
import org.eclipse.ditto.internal.utils.persistence.mongo.config.SnapshotConfig;
import org.eclipse.ditto.internal.utils.persistentactors.AbstractPersistenceActor;
import org.eclipse.ditto.internal.utils.persistentactors.commands.CommandStrategy;
import org.eclipse.ditto.internal.utils.persistentactors.commands.DefaultContext;
import org.eclipse.ditto.internal.utils.persistentactors.events.EventStrategy;
import org.eclipse.ditto.internal.utils.pubsub.DistributedPub;
import org.eclipse.ditto.internal.utils.pubsub.extractors.AckExtractor;
import org.eclipse.ditto.json.JsonFactory;
import org.eclipse.ditto.things.api.commands.sudo.SudoRetrieveThing;
import org.eclipse.ditto.things.model.Thing;
import org.eclipse.ditto.things.model.ThingBuilder;
import org.eclipse.ditto.things.model.ThingConstants;
import org.eclipse.ditto.things.model.ThingId;
import org.eclipse.ditto.things.model.ThingLifecycle;
import org.eclipse.ditto.things.model.ThingsModelFactory;
import org.eclipse.ditto.things.model.signals.commands.exceptions.ThingNotAccessibleException;
import org.eclipse.ditto.things.model.signals.commands.modify.CreateThing;
import org.eclipse.ditto.things.model.signals.commands.query.RetrieveThing;
import org.eclipse.ditto.things.model.signals.commands.query.ThingQueryCommandResponse;
import org.eclipse.ditto.things.model.signals.events.ThingEvent;
import org.eclipse.ditto.things.service.common.config.DittoThingsConfig;
import org.eclipse.ditto.things.service.common.config.ThingConfig;
import org.eclipse.ditto.things.service.persistence.actors.strategies.commands.ThingCommandStrategies;
import org.eclipse.ditto.things.service.persistence.actors.strategies.events.ThingEventStrategies;

import akka.actor.Props;
import akka.japi.pf.ReceiveBuilder;
import akka.persistence.RecoveryCompleted;

/**
 * PersistentActor which "knows" the state of a single {@link Thing}.
 */
public final class ThingPersistenceActor
        extends AbstractPersistenceActor<Command<?>, Thing, ThingId, ThingId, ThingEvent<?>> {

    /**
     * The prefix of the persistenceId for Things.
     */
    static final String PERSISTENCE_ID_PREFIX = ThingConstants.ENTITY_TYPE + ":";

    /**
     * The ID of the journal plugin this persistence actor uses.
     */
    static final String JOURNAL_PLUGIN_ID = "akka-contrib-mongodb-persistence-things-journal";

    /**
     * The ID of the snapshot plugin this persistence actor uses.
     */
    static final String SNAPSHOT_PLUGIN_ID = "akka-contrib-mongodb-persistence-things-snapshots";

    private static final AckExtractor<ThingEvent<?>> ACK_EXTRACTOR =
            AckExtractor.of(ThingEvent::getEntityId, ThingEvent::getDittoHeaders);

    private final ThingConfig thingConfig;
    private final DistributedPub<ThingEvent<?>> distributedPub;

    @SuppressWarnings("unused")
    private ThingPersistenceActor(final ThingId thingId,
            final DistributedPub<ThingEvent<?>> distributedPub) {

        super(thingId);
        final DittoThingsConfig thingsConfig = DittoThingsConfig.of(
                DefaultScopedConfig.dittoScoped(getContext().getSystem().settings().config())
        );
        thingConfig = thingsConfig.getThingConfig();
        this.distributedPub = distributedPub;
    }

    /**
     * Creates Akka configuration object {@link Props} for this ThingPersistenceActor.
     *
     * @param thingId the Thing ID this Actor manages.
     * @param distributedPub the distributed-pub access to publish thing events.
     * @return the Akka configuration Props object
     */
    public static Props props(final ThingId thingId,
            final DistributedPub<ThingEvent<?>> distributedPub) {

        return Props.create(ThingPersistenceActor.class, thingId, distributedPub);
    }

    @Override
    public void onQuery(final Command<?> command, final WithDittoHeaders response) {
        if (response.getDittoHeaders().didLiveChannelConditionMatch()) {
            final var liveChannelTimeoutStrategy = response.getDittoHeaders()
                    .getLiveChannelTimeoutStrategy()
                    .orElse(LiveChannelTimeoutStrategy.FAIL);
            if (liveChannelTimeoutStrategy != LiveChannelTimeoutStrategy.USE_TWIN &&
                    response instanceof ThingQueryCommandResponse<?> queryResponse) {
                super.onQuery(command, queryResponse.setEntity(JsonFactory.nullLiteral()));
                return;
            }
        }
        super.onQuery(command, response);
    }

    @Override
    public String persistenceId() {
        return entityId.getEntityType() + ":" + entityId;
    }

    @Override
    public String journalPluginId() {
        return JOURNAL_PLUGIN_ID;
    }

    @Override
    public String snapshotPluginId() {
        return SNAPSHOT_PLUGIN_ID;
    }

    @Override
    protected Class<?> getEventClass() {
        return ThingEvent.class;
    }

    @Override
    protected CommandStrategy.Context<ThingId> getStrategyContext() {
        return DefaultContext.getInstance(entityId, log);
    }

    @Override
    protected ThingCommandStrategies getCreatedStrategy() {
        return ThingCommandStrategies.getInstance(getContext().getSystem());
    }

    @Override
    protected CommandStrategy<CreateThing, Thing, ThingId, ThingEvent<?>> getDeletedStrategy() {
        return ThingCommandStrategies.getCreateThingStrategy(getContext().getSystem());
    }

    @Override
    protected EventStrategy<ThingEvent<?>, Thing> getEventStrategy() {
        return ThingEventStrategies.getInstance();
    }

    @Override
    protected ActivityCheckConfig getActivityCheckConfig() {
        return thingConfig.getActivityCheckConfig();
    }

    @Override
    protected SnapshotConfig getSnapshotConfig() {
        return thingConfig.getSnapshotConfig();
    }

    @Override
    protected boolean entityExistsAsDeleted() {
        return null != entity && entity.hasLifecycle(ThingLifecycle.DELETED);
    }

    @Override
    protected Receive matchAnyWhenDeleted() {
        return ReceiveBuilder.create()
                .match(RetrieveThing.class, this::handleByCommandStrategy)
                .match(SudoRetrieveThing.class, this::handleByCommandStrategy)
                .build()
                .orElse(super.matchAnyWhenDeleted());
    }

    @Override
    protected DittoRuntimeExceptionBuilder<?> newNotAccessibleExceptionBuilder() {
        return ThingNotAccessibleException.newBuilder(entityId);
    }

    @Override
    protected void recoveryCompleted(final RecoveryCompleted event) {
        if (entity != null) {
            entity = enhanceThingWithLifecycle(entity);
            log.info("Thing <{}> was recovered.", entityId);
        }
        super.recoveryCompleted(event);
    }

    @Override
    protected void publishEvent(@Nullable final Thing previousEntity, final ThingEvent<?> event) {
        distributedPub.publishWithAcks(event, ACK_EXTRACTOR, getSelf());
    }

    @Override
    protected boolean shouldSendResponse(final DittoHeaders dittoHeaders) {
        return dittoHeaders.isResponseRequired() ||
                dittoHeaders.getAcknowledgementRequests()
                        .stream()
                        .anyMatch(ar -> DittoAcknowledgementLabel.TWIN_PERSISTED.equals(ar.getLabel()));
    }

    @Override
    protected boolean isEntityAlwaysAlive() {
        return false;
    }

    @Override
    protected JsonSchemaVersion getEntitySchemaVersion(final Thing entity) {
        return entity.getImplementedSchemaVersion();
    }

    private static Thing enhanceThingWithLifecycle(final Thing thing) {
        final ThingBuilder.FromCopy thingBuilder = ThingsModelFactory.newThingBuilder(thing);
        if (thing.getLifecycle().isEmpty()) {
            thingBuilder.setLifecycle(ThingLifecycle.ACTIVE);
        }

        return thingBuilder.build();
    }
}
